// Python interface to meshfix via nanobind.
#include <cstring>
#include <iostream>
#include <stdexcept>

#include <nanobind/nanobind.h>
#include <nanobind/ndarray.h>
#include <nanobind/stl/string.h>
#include <nanobind/stl/vector.h>
// #include <stdio.h>

#include "array_support.h"
#include "tmesh.h"

using namespace T_MESH;

#define TVI1(a) (TMESH_TO_INT(((Triangle *)a->data)->v1()->x))
#define TVI2(a) (TMESH_TO_INT(((Triangle *)a->data)->v2()->x))
#define TVI3(a) (TMESH_TO_INT(((Triangle *)a->data)->v3()->x))

double closestPair(List *bl1, List *bl2, Vertex **closest_on_bl1, Vertex **closest_on_bl2) {
    Node *n, *m;
    Vertex *v, *w;
    double adist, mindist = DBL_MAX;

    FOREACHVVVERTEX(bl1, v, n)
    FOREACHVVVERTEX(bl2, w, m)
    if ((adist = w->squaredDistance(v)) < mindist) {
        mindist = adist;
        *closest_on_bl1 = v;
        *closest_on_bl2 = w;
    }

    return mindist;
}

bool joinClosestComponents(Basic_TMesh *tin) {
    Vertex *v, *w, *gv, *gw;
    Triangle *t, *s;
    Node *n;
    List triList, boundary_loops, *one_loop;
    List **bloops_array;
    int i, j, numloops;

    // Mark triangles with connected component's unique ID
    i = 0;
    FOREACHVTTRIANGLE((&(tin->T)), t, n) t->info = NULL;
    FOREACHVTTRIANGLE((&(tin->T)), t, n) if (t->info == NULL) {
        i++;
        triList.appendHead(t);
        t->info = (void *)(intptr_t)i;

        while (triList.numels()) {
            t = (Triangle *)triList.popHead();
            if ((s = t->t1()) != NULL && s->info == NULL) {
                triList.appendHead(s);
                s->info = (void *)(intptr_t)i;
            }
            if ((s = t->t2()) != NULL && s->info == NULL) {
                triList.appendHead(s);
                s->info = (void *)(intptr_t)i;
            }
            if ((s = t->t3()) != NULL && s->info == NULL) {
                triList.appendHead(s);
                s->info = (void *)(intptr_t)i;
            }
        }
    }

    if (i < 2) {
        FOREACHVTTRIANGLE((&(tin->T)), t, n) t->info = NULL;
        //   JMesh::info("Mesh is a single component. Nothing done.");
        return false;
    }

    FOREACHVTTRIANGLE((&(tin->T)), t, n) {
        t->v1()->info = t->v2()->info = t->v3()->info = t->info;
    }

    FOREACHVVVERTEX((&(tin->V)), v, n) if (!IS_VISITED2(v) && v->isOnBoundary()) {
        w = v;
        one_loop = new List;
        do {
            one_loop->appendHead(w);
            MARK_VISIT2(w);
            w = w->nextOnBoundary();
        } while (w != v);
        boundary_loops.appendHead(one_loop);
    }
    FOREACHVVVERTEX((&(tin->V)), v, n) UNMARK_VISIT2(v);

    bloops_array = (List **)boundary_loops.toArray();
    numloops = boundary_loops.numels();

    int numtris = tin->T.numels();
    double adist, mindist = DBL_MAX;

    gv = NULL;
    for (i = 0; i < numloops; i++)
        for (j = 0; j < numloops; j++)
            if (((Vertex *)bloops_array[i]->head()->data)->info !=
                ((Vertex *)bloops_array[j]->head()->data)->info) {
                adist = closestPair(bloops_array[i], bloops_array[j], &v, &w);
                if (adist < mindist) {
                    mindist = adist;
                    gv = v;
                    gw = w;
                }
            }

    if (gv != NULL)
        tin->joinBoundaryLoops(gv, gw, 1, 0);

    FOREACHVTTRIANGLE((&(tin->T)), t, n) t->info = NULL;
    FOREACHVVVERTEX((&(tin->V)), v, n) v->info = NULL;

    free(bloops_array);
    while ((one_loop = (List *)boundary_loops.popHead()) != NULL)
        delete one_loop;

    return (gv != NULL);
}

class PyTMesh : public Basic_TMesh {

  public:
    T_MESH::Basic_TMesh tmesh;

    PyTMesh() { tmesh = T_MESH::Basic_TMesh(); }

    void load_file(std::string filename_str, bool fix_connectivity = true) {
        if (V.numels()) {
            throw std::runtime_error(
                "Cannot load a mesh after points have already been loaded");
        }

        const char *filename = filename_str.c_str();
        int ret = load(filename);
        if (ret) {
            throw std::runtime_error("Failed to load mesh file");
        }
        d_boundaries = d_handles = d_shells = 1;
    }

    // Save cleaned mesh to file

    // The file format is deduced from one of the following filename
    // extensions:

    //     - ``"wrl"`` - vrml 1.0
    //     - ``"iv"`` - OpenInventor
    //     - ``"off"`` - Object file format
    //     - ``"ply"`` - PLY format
    //     - ``"tri"`` - IMATI Ver-Tri

    // If 'back_approx' is set to True, vertex coordinates are approximated
    // to reflect the limited precision of floating point
    // representation in ASCII files. This should be used when
    // coherence is necessary between in-memory and saved data.
    // A non-zero return value is returned if errors occur.
    void save_file(std::string filename_str, bool back_approx = false) {
        if (!V.numels()) {
            throw std::runtime_error("This mesh contains no points");
        }

        const char *filename = filename_str.c_str();
        int ret = save(filename);
        if (ret) {
            throw std::runtime_error("Failed to save mesh file");
        }
    }

    void load_array(
        const NDArray<const double, 2> point_arr,
        const NDArray<const int, 2> face_arr,
        bool fix_connectivity = true) {

        if (V.numels()) {
            throw std::runtime_error(
                "Cannot load arrays after points have already been loaded");
        }

        // point_arr.shape(0), point_arr.data(), face_arr.shape(0), face_arr.data());
        int nv = point_arr.shape(0);
        const double *points = point_arr.data();
        int nt = face_arr.shape(0);
        const int *faces = face_arr.data();

        Vertex *v;
        Node *n;
        int i;

        // Parse vertices
        for (i = 0; i < nv; i++) {
            V.appendTail(newVertex(points[i * 3], points[i * 3 + 1], points[i * 3 + 2]));
        }

        // Initialize triangle indexing array
        ExtVertex **var = (ExtVertex **)malloc(sizeof(ExtVertex *) * nv);
        i = 0;
        FOREACHVERTEX(v, n) var[i++] = new ExtVertex(v);

        // Load triangles
        for (i = 0; i < nt; i++) {
            CreateIndexedTriangle(var, faces[i * 3], faces[i * 3 + 1], faces[i * 3 + 2]);
        }

        // Memory management
        for (i = 0; i < nv; i++)
            delete (var[i]);
        free(var);

        // TMesh::info("Loaded %d vertices and %d faces.\n", nv, nt);

        if (fix_connectivity) {
            fixConnectivity();
        }
        d_boundaries = d_handles = d_shells = 1;
    }

    void fix_connectivity() { fixConnectivity(); }

    // Return the number of faces in mesh
    int n_faces() { return T.numels(); }
    int n_points() { return V.numels(); }

    // Enable/disable console print out
    void set_quiet(int quiet) { TMesh::quiet = quiet; }

    // Joins multiple open components
    void join_closest_components() {
        TMesh::begin_progress();
        while (joinClosestComponents(this))
            TMesh::report_progress("Num. components: %d       ", this->shells());
        TMesh::end_progress();
        this->deselectTriangles();
    }

    // return points and faces arrays
    nb::tuple return_arrays() {
        Node *n;
        Vertex *v;
        coord *ocds;
        int i;

        int n_points = V.numels();
        NDArray<double, 2> points_arr = MakeNDArray<double, 2>({n_points, 3});
        double *points = points_arr.data();

        // Populate points
        int c = 0;
        FOREACHVERTEX(v, n) {
            points[c] = v->x;
            points[c + 1] = v->y;
            points[c + 2] = v->z;
            c += 3;
        }

        ocds = new coord[V.numels()];
        i = 0;
        FOREACHVERTEX(v, n) ocds[i++] = v->x;
        i = 0;
        FOREACHVERTEX(v, n) v->x = i++;

        int n_faces = T.numels();
        NDArray<int, 2> faces_arr = MakeNDArray<int, 2>({n_faces, 3});
        int *faces = faces_arr.data();

        // Populate faces
        c = 0;
        FOREACHNODE(T, n) {
            faces[c] = TVI1(n);
            faces[c + 1] = TVI2(n);
            faces[c + 2] = TVI3(n);
            c += 3;
        }

        // clean up
        i = 0;
        FOREACHVERTEX(v, n) v->x = ocds[i++];
        delete[] ocds;

        return nb::make_tuple(points_arr, faces_arr);
    }

    int n_boundaries() { return boundaries(); }

    void _boundaries() {
        throw std::runtime_error("`boundaries()` is deprecated. Use `n_boundaries` instead.");
    }

    // Remove self-intersections and degenerate faces.

    // Iteratively call strongDegeneracyRemoval and
    // strongIntersectionRemoval to produce an eventually clean mesh
    // without degeneracies and intersections.  The two
    // aforementioned methods are called up to max_iter times and
    // each of them is called using 'inner_loops' as a parameter.
    // Returns true only if the mesh could be completely cleaned.
    bool clean(int max_iters = 10, int inner_loops = 3) {
        return meshclean(max_iters, inner_loops);
    }

    // Fill small boundaries.

    // Fills all the holes having less than ``nbe`` boundary
    // edges. If ``refine`` is true, adds inner vertices to reproduce
    // the sampling density of the surroundings. Returns number of
    // holes patched.  If 'nbe' is 0 (default), all the holes are
    // patched.
    int fill_small_boundaries(int nbe = 0, bool refine = true) {
        return fillSmallBoundaries(nbe, refine);
    }

    // Selects all intersecting triangles.
    // Selects all the triangles that improperly intersect other
    // parts of the mesh and return their number. The parameter
    // 'tris_per_cell' determines the depth of the recursive space
    // subdivision used to keep the complexity under a reasonable
    // threshold. The default value is safe in most cases.
    //
    // If ``justproper`` is true, coincident edges and vertices are not
    // regarded as intersections even if they are not common
    // subsimplexes.
    NDArray<int, 2>
    select_intersecting_triangles(int tris_per_cell = 50, bool justproper = false) {
        // Return the number of intersecting triangles
        int n_intersecting = selectIntersectingTriangles(tris_per_cell, justproper);

        // Create a face array and populate it with the intersecting faces
        NDArray<int, 2> faces_arr = MakeNDArray<int, 2>({n_intersecting, 3});
        int *faces = faces_arr.data();

        // populate the array
        Node *n;
        Triangle *t;

        int c = 0;
        int i = 0;
        FOREACHTRIANGLE(t, n) {
            if (IS_VISITED(t)) {
                faces[i] = c;
                i++;
            }
            c++;
        }

        return faces_arr;
    }

    int remove_smallest_components() { return removeSmallestComponents(); };

}; // class

void repair(
    PyTMesh &tin,
    bool verbose = false,
    bool joincomp = true,
    bool remove_smallest_components = true) {

    if (remove_smallest_components) {
        int sc = tin.remove_smallest_components();
        if (sc && verbose) {
            std::cout << "Removed " << sc << " small components\n";
        }
    }

    if (joincomp) {
        tin.join_closest_components();
    }

    if (tin.n_boundaries()) {
        if (verbose) {
            std::cout << "Patching holes...\n";
        }
        int holespatched = tin.fill_small_boundaries();
        if (verbose) {
            std::cout << "Patched " << holespatched << " holes\n";
        }
    }

    if (verbose) {
        std::cout << "Fixing degeneracies and intersections\n";
    }

    bool result = tin.clean();

    if (tin.n_boundaries()) {
        if (verbose) {
            std::cout << "Patching holes...\n";
        }
        int holespatched = tin.fill_small_boundaries();
        if (verbose) {
            std::cout << "Patched " << holespatched << " holes\n";
        }

        if (verbose) {
            std::cout << "Performing final check...\n";
        }
        result = tin.clean();
    }

    if (result) {
        std::cerr << "MeshFix could not fix everything\n";
    }
}

void clean_from_file_cpp(
    const std::string &infile,
    const std::string &outfile,
    bool verbose = false,
    bool joincomp = false) {

    PyTMesh tin;

    tin.set_quiet(verbose ? 0 : 1);
    tin.load_file(infile, true);

    if (joincomp) {
        tin.join_closest_components();
    }

    repair(tin, verbose, joincomp);

    tin.save_file(outfile, false);
}

NB_MODULE(_meshfix, m) { // "_meshfix" must match library name from CMakeLists.txt
    nb::class_<PyTMesh>(m, "PyTMesh")
        .def(nb::init<>())
        .def_prop_ro("n_boundaries", &PyTMesh::n_boundaries)
        .def_prop_ro("n_faces", &PyTMesh::n_faces)
        .def_prop_ro("n_points", &PyTMesh::n_points)
        .def("join_closest_components", &PyTMesh::join_closest_components)
        .def("set_quiet", &PyTMesh::set_quiet)
        .def("fix_connectivity", &PyTMesh::fix_connectivity)
        .def("return_arrays", &PyTMesh::return_arrays)
        .def(
            "load_file",
            &PyTMesh::load_file,
            nb::arg("filename"),
            nb::arg("fix_connectivity") = true)
        .def(
            "fill_small_boundaries",
            &PyTMesh::fill_small_boundaries,
            nb::arg("nbe") = 0,
            nb::arg("refine") = true)
        .def("clean", &PyTMesh::clean, nb::arg("max_iters") = 10, nb::arg("inner_loops") = 3)
        .def("boundaries", &PyTMesh::_boundaries)
        .def(
            "save_file",
            &PyTMesh::save_file,
            nb::arg("filename"),
            nb::arg("back_approx") = false)
        .def("boundaries", &PyTMesh::_boundaries)
        .def(
            "select_intersecting_triangles",
            &PyTMesh::select_intersecting_triangles,
            nb::arg("tris_per_cell") = 50,
            nb::arg("justproper") = false)
        .def("remove_smallest_components", &PyTMesh::remove_smallest_components)
        .def(
            "load_array",
            &PyTMesh::load_array,
            nb::arg("points_arr"),
            nb::arg("faces_arr"),
            nb::arg("fix_connectivity") = true);

    m.def(
        "clean_from_file",
        &clean_from_file_cpp,
        nb::arg("infile"),
        nb::arg("outfile"),
        nb::arg("verbose") = false,
        nb::arg("joincomp") = false);
}
