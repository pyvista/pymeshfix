// Python interface to meshfix via nanobind.
#include <cstring>
#include <iostream>
#include <stdexcept>

#include <nanobind/nanobind.h>
#include <nanobind/ndarray.h>
#include <nanobind/stl/string.h>
#include <nanobind/stl/vector.h>

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

    void load_file(std::string filename_str) {
        if (V.numels()) {
            throw std::runtime_error(
                "Cannot load a mesh after points have already been loaded");
        }

        const char *filename = filename_str.c_str();
        int ret = load(filename);
        if (ret) {
            throw std::runtime_error("Failed to load mesh file");
        }
    }

    // Save cleaned mesh to file
    //
    // The file format is deduced from one of the following filename
    // extensions:
    //
    //     - ``"wrl"`` - vrml 1.0
    //     - ``"iv"`` - OpenInventor
    //     - ``"off"`` - Object file format
    //     - ``"ply"`` - PLY format
    //     - ``"tri"`` - IMATI Ver-Tri
    //
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
        const NDArray<const double, 2> point_arr, const NDArray<const int, 2> face_arr) {

        if (V.numels()) {
            throw std::runtime_error(
                "Cannot load arrays after arrays have already been loaded");
        }

        if (point_arr.shape(1) != 3) {
            throw std::runtime_error("Point array must have shape (N,3)");
        }
        if (face_arr.shape(1) != 3) {
            throw std::runtime_error("Face array must have shape (M,3)");
        }

        const size_t nv = point_arr.shape(0);
        const size_t nt = face_arr.shape(0);

        // Load vertices
        for (size_t i = 0; i < nv; ++i) {
            double x = point_arr(i, 0);
            double y = point_arr(i, 1);
            double z = point_arr(i, 2);
            V.appendTail(newVertex(x, y, z));
        }

        // Create ExtVertex array for indexed triangles
        ExtVertex **var = (ExtVertex **)malloc(sizeof(ExtVertex *) * nv);
        size_t idx = 0;
        Node *n;
        Vertex *v;
        FOREACHVERTEX(v, n) var[idx++] = new ExtVertex(v);

        // Load faces
        TMesh::begin_progress();
        for (size_t i = 0; i < nt; ++i) {
            const int *f = &face_arr(i, 0);
            int i4 = face_arr.shape(1); // number of indices in this face
            if (i4 < 3) {
                TMesh::warning("Face %d has fewer than 3 vertices. Skipping.", i);
                continue;
            }

            int i1 = f[0];
            int i2 = f[1];
            int i3;

            for (int j = 2; j < i4; ++j) {
                i3 = f[j];

                if (i1 == i2 || i2 == i3 || i3 == i1) {
                    TMesh::warning("Coincident indices at triangle %d. Skipping.", i);
                } else if (!CreateIndexedTriangle(var, i1, i2, i3)) {
                    TMesh::warning("Failed to create triangle at face %d. Skipping.", i);
                }

                i2 = i3;
            }

            if ((i % 1000) == 0) {
                TMesh::report_progress("Loading ..%d%%", (int)((i * 100) / nt));
            }
        }
        TMesh::end_progress();

        // Optional connectivity fix
        fixConnectivity();
        eulerUpdate();
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

    NDArray<double, 2> return_points() {
        Node *n;
        Vertex *v;

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

        return points_arr;
    }

    NDArray<int, 2> return_faces() {
        Node *n;
        Vertex *v;
        coord *ocds;
        int i, c;

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

        return faces_arr;
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

    bool strong_degeneracy_removal(int max_iters) {
        return strongDegeneracyRemoval(max_iters);
    };
    bool strong_intersection_removal(int max_iters) {
        return strongIntersectionRemoval(max_iters);
    };

    // Fill small boundaries.
    //
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

void clean_from_file(
    const std::string &infile,
    const std::string &outfile,
    bool verbose = false,
    bool joincomp = false) {

    PyTMesh tin;

    tin.set_quiet(!verbose);
    tin.load_file(infile);
    repair(tin, verbose, joincomp);

    tin.save_file(outfile, false);
}

nb::tuple clean_from_arrays(
    const NDArray<const double, 2> v,
    const NDArray<const int, 2> f,
    bool verbose = false,
    bool joincomp = false,
    bool remove_smallest_components = true) {

    PyTMesh tin;

    tin.set_quiet(!verbose);
    tin.load_array(v, f);
    repair(tin, verbose, joincomp, remove_smallest_components);

    return tin.return_arrays();
}

NB_MODULE(_meshfix, m) { // "_meshfix" must match library name from CMakeLists.txt
    nb::class_<PyTMesh>(
        m,
        "PyTMesh",
        R"doc(
Mesh repair and cleaning class.

Wraps the MeshFix Basic_TMesh functionality and exposes it to Python.
Provides methods to inspect, repair, and extract mesh data.
)doc")
        .def(nb::init<>())
        .def_prop_ro(
            "n_boundaries",
            &PyTMesh::n_boundaries,
            R"doc(
Number of boundary loops in the mesh.
)doc")
        .def_prop_ro(
            "n_faces",
            &PyTMesh::n_faces,
            R"doc(
Number of faces in the mesh.
)doc")
        .def_prop_ro(
            "n_points",
            &PyTMesh::n_points,
            R"doc(
Number of points in the mesh.
)doc")
        .def(
            "join_closest_components",
            &PyTMesh::join_closest_components,
            R"doc(
Join the closest disconnected mesh components.
)doc")
        .def(
            "set_quiet",
            &PyTMesh::set_quiet,
            R"doc(
Enable or disable console output.

Parameters
----------
quiet : bool
    If True, suppress output.
)doc")
        .def(
            "fix_connectivity",
            &PyTMesh::fix_connectivity,
            R"doc(
Repair mesh connectivity issues.
)doc")
        .def(
            "return_arrays",
            &PyTMesh::return_arrays,
            R"doc(
Return mesh data as vertex and face arrays.

Returns
-------
numpy.ndarray
    Vertex array of shape (N, 3).
numpy.ndarray
    Face array of shape (M, 3).
)doc")
        .def(
            "return_points",
            &PyTMesh::return_points,
            R"doc(
Return the vertex array.

Returns
-------
numpy.ndarray
    Vertex array of shape ``(N, 3)``.
)doc")
        .def(
            "strong_intersection_removal",
            &PyTMesh::strong_intersection_removal,
            R"doc(
Iteratively removes self-intersecting triangles.
)doc")
        .def(
            "strong_degeneracy_removal",
            &PyTMesh::strong_degeneracy_removal,
            R"doc(
Iteratively removes degenerate triangles and closes holes.
)doc")
        .def(
            "return_faces",
            &PyTMesh::return_faces,
            R"doc(
Return the face array.

Returns
-------
numpy.ndarray[np.int32]
    Fase array of shape ``(M, 3)``.
)doc")
        .def(
            "load_file",
            &PyTMesh::load_file,
            R"doc(
Load a surface mesh from a file.

Parameters
----------
filename : str
    Path to the input mesh file.
)doc",
            nb::arg("filename"))
        .def(
            "fill_small_boundaries",
            &PyTMesh::fill_small_boundaries,
            R"doc(
Fill small boundary loops (holes) in the mesh.

Parameters
----------
nbe : int, default: 0
    Maximum number of boundary edges to fill. If 0, fill all.
refine : bool, default: True
    Refine filled regions.
)doc",
            nb::arg("nbe") = 0,
            nb::arg("refine") = true)
        .def(
            "clean",
            &PyTMesh::clean,
            R"doc(
Perform iterative mesh cleaning and repair.

Parameters
----------
max_iters : int, default: 10
    Maximum number of cleaning iterations.
inner_loops : int, default: 3
    Number of inner optimization loops per iteration.
)doc",
            nb::arg("max_iters") = 10,
            nb::arg("inner_loops") = 3)
        .def("boundaries", &PyTMesh::_boundaries)
        .def(
            "save_file",
            &PyTMesh::save_file,
            R"doc(
Save the mesh to a file.

Parameters
----------
filename : str
    Output filename.
back_approx : bool, default: False
    Use backward approximation when writing.
)doc",
            nb::arg("filename"),
            nb::arg("back_approx") = false)
        .def("boundaries", &PyTMesh::_boundaries)
        .def(
            "select_intersecting_triangles",
            &PyTMesh::select_intersecting_triangles,
            R"doc(
Select intersecting triangles in the mesh.

Parameters
----------
tris_per_cell : int, default: 50
    The depth of the recursive space subdivision used to keep
    the complexity under a reasonable threshold. The default value
    is safe in most cases.

justproper : bool, default: False
    If ``justproper`` is true, coincident edges and vertices are not
    regarded as intersections even if they are not common
    subsimplexes.

Returns
-------
np.ndarray[np.int32]
   Face array shaped ``(m, 3)`` of self-intersecting triangles.

)doc",
            nb::arg("tris_per_cell") = 50,
            nb::arg("justproper") = false)
        .def(
            "remove_smallest_components",
            &PyTMesh::remove_smallest_components,
            R"doc(
Remove all but the largest connected mesh component.
)doc")
        .def(
            "load_array",
            &PyTMesh::load_array,
            R"doc(
Load a surface mesh from vertex and face arrays.

Parameters
----------
points_arr : numpy.ndarray
    Vertex array of shape ``(n, 3)``.
faces_arr : numpy.ndarray
    Face array of shape ``(m, 3)``.
)doc",
            nb::arg("points_arr"),
            nb::arg("faces_arr") = false);

    m.def(
        "clean_from_arrays",
        &clean_from_arrays,
        R"doc(
Clean and repair a triangular surface mesh from vertex and face arrays.

Parameters
----------
v : numpy.ndarray[np.float64]
    Vertex array of shape ``(n, 3)``.
f : numpy.ndarray[np.int32]
    Face array of shape ``(m, 3)``.
verbose : bool, default: False
    Enable verbose output.
joincomp : bool, default: False
    Attempt to join nearby open components.
remove_smallest_components : bool, default: True
    Remove all but the largest connected component before repair.

Returns
-------
numpy.ndarray
    Cleaned vertex array.
numpy.ndarray
    Cleaned face array.

Examples
--------
>>> import pymeshfix
>>> import numpy as np
>>> points = np.load('points.npy')
>>> faces = np.load('faces.npy')
>>> clean_points, clean_faces = pymeshfix.clean_from_arrays(points, faces)

)doc",
        nb::arg("v"),
        nb::arg("f"),
        nb::arg("verbose") = false,
        nb::arg("joincomp") = false,
        nb::arg("remove_smallest_components") = true);

    m.def(
        "clean_from_file",
        &clean_from_file,
        R"doc(
Clean and repair a triangular surface mesh from a file.

Parameters
----------
infile : str
    Input mesh filename.
outfile : str
    Output mesh filename.
verbose : bool, default: False
    Enable verbose output.
joincomp : bool, default False
    Attempt to join nearby open components.

Examples
--------
Clean a mesh without using pyvista or vtk.

>>> import pymeshfix
>>> pymeshfix.clean_from_file('inmesh.ply', 'outmesh.ply')

)doc",
        nb::arg("infile"),
        nb::arg("outfile"),
        nb::arg("verbose") = false,
        nb::arg("joincomp") = false);
}
