#include "tmesh.h"
#include "meshfix.h"
#include <stdlib.h>
#include <string.h>
#include <time.h>

using namespace T_MESH;

#define TVI1(a) (TMESH_TO_INT(((Triangle *)a->data)->v1()->x))
#define TVI2(a) (TMESH_TO_INT(((Triangle *)a->data)->v2()->x))
#define TVI3(a) (TMESH_TO_INT(((Triangle *)a->data)->v3()->x))

// class
Basic_TMesh_wrap::Basic_TMesh_wrap()
{};

double closestPair(List *bl1, List *bl2, Vertex **closest_on_bl1, Vertex **closest_on_bl2)
{
	Node *n, *m;
	Vertex *v, *w;
	double adist, mindist = DBL_MAX;

	FOREACHVVVERTEX(bl1, v, n)
		FOREACHVVVERTEX(bl2, w, m)
	if ((adist = w->squaredDistance(v))<mindist)
	{
		mindist = adist;
		*closest_on_bl1 = v;
		*closest_on_bl2 = w;
	}

	return mindist;
}

bool joinClosestComponents(Basic_TMesh *tin)
{
	Vertex *v, *w, *gv, *gw;
	Triangle *t, *s;
	Node *n;
	List triList, boundary_loops, *one_loop;
	List **bloops_array;
	int i, j, numloops;

	// Mark triangles with connected component's unique ID
	i = 0;
	FOREACHVTTRIANGLE((&(tin->T)), t, n) t->info = NULL;
	FOREACHVTTRIANGLE((&(tin->T)), t, n) if (t->info == NULL)
	{
		i++;
		triList.appendHead(t);
		t->info = (void *)(intptr_t)i;

		while (triList.numels())
		{
			t = (Triangle *)triList.popHead();
			if ((s = t->t1()) != NULL && s->info == NULL) { triList.appendHead(s); s->info = (void *)(intptr_t)i; }
			if ((s = t->t2()) != NULL && s->info == NULL) { triList.appendHead(s); s->info = (void *)(intptr_t)i; }
			if ((s = t->t3()) != NULL && s->info == NULL) { triList.appendHead(s); s->info = (void *)(intptr_t)i; }
		}
	}

	if (i<2)
	{
		FOREACHVTTRIANGLE((&(tin->T)), t, n) t->info = NULL;
		//   JMesh::info("Mesh is a single component. Nothing done.");
		return false;
	}

	FOREACHVTTRIANGLE((&(tin->T)), t, n)
	{
		t->v1()->info = t->v2()->info = t->v3()->info = t->info;
	}

	FOREACHVVVERTEX((&(tin->V)), v, n) if (!IS_VISITED2(v) && v->isOnBoundary())
	{
		w = v;
		one_loop = new List;
		do
		{
			one_loop->appendHead(w); MARK_VISIT2(w);
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
	for (i = 0; i<numloops; i++)
	for (j = 0; j<numloops; j++)
	if (((Vertex *)bloops_array[i]->head()->data)->info != ((Vertex *)bloops_array[j]->head()->data)->info)
	{
		adist = closestPair(bloops_array[i], bloops_array[j], &v, &w);
		if (adist<mindist) { mindist = adist; gv = v; gw = w; }
	}

	if (gv != NULL) tin->joinBoundaryLoops(gv, gw, 1, 0);

	FOREACHVTTRIANGLE((&(tin->T)), t, n) t->info = NULL;
	FOREACHVVVERTEX((&(tin->V)), v, n) v->info = NULL;

	free(bloops_array);
	while ((one_loop = (List *)boundary_loops.popHead()) != NULL) delete one_loop;

	return (gv != NULL);
}

void usage()
{
 printf("\nMeshFix V2.0 - by Marco Attene\n------\n");
 printf("Usage: MeshFix inmeshfile [outmeshfile] [-a] [-j] [-x]\n");
 printf("  Processes 'inmeshfile' and saves the result to 'outmeshfile'\n");
 printf("  If 'outmeshfile' is not specified 'inmeshfile_fixed.off' will be produced\n");
 printf("  Option '-a' = joins multiple open components before starting\n");
 printf("  Option '-j' = output files in STL format insted of OFF\n");
 printf("  Option '-x' exits if output file already exists.\n");
 printf("  Accepted input formats are OFF, PLY and STL.\n  Other formats are supported only partially.\n");
 printf("\nIf MeshFix is used for research purposes, please cite the following paper:\n");
 printf("\n   M. Attene.\n   A lightweight approach to repairing digitized polygon meshes.\n   The Visual Computer, 2010. (c) Springer.\n");
 printf("\nHIT ENTER TO EXIT.\n");
 getchar();
 exit(0);
}

char *createFilename(const char *iname, const char *subext, char *oname, const char *newextension)
{
	static char tname[2048];
	strcpy(tname, iname);
	for (int n = strlen(tname) - 1; n>0; n--) if (tname[n] == '.') { tname[n] = '\0'; break; }
	sprintf(oname, "%s%s%s", tname, subext, newextension);
	return oname;
}


int main(int argc, char *argv[])
{
 TMesh::init(); // This is mandatory
 TMesh::app_name = "MeshFix";
 TMesh::app_version = "2.0";
 TMesh::app_year = "2016";
 TMesh::app_authors = "Marco Attene";
 TMesh::app_maillist = "attene@ge.imati.cnr.it";

 clock_t beginning = clock();

 // Uncomment the following to prevent message reporting
 // TMesh::quiet = true;

 Basic_TMesh tin;
 bool stl_output = false;
 bool skip_if_fixed = false;
 bool join_multiple_components = false;
 char infilename[2048], outfilename[2048], extension[] = ".off";

 if (argc < 2) usage();

 float par;
 int i = 2;
 if (argc > 2 && argv[2][0] == '-') i--;

 for (; i<argc; i++)
 {
  if (i<argc-1) par = (float)atof(argv[i+1]); else par = 0;
  if (!strcmp(argv[i], "-x")) skip_if_fixed = true;
  else if (!strcmp(argv[i], "-a")) join_multiple_components = true;
  else if (!strcmp(argv[i], "-j")) stl_output = true;
  else if (argv[i][0] == '-') TMesh::warning("%s - Unknown operation.\n", argv[i]);

  if (par) i++;
 }

 sprintf(infilename, "%s", argv[1]);
 if (stl_output) strcpy(extension, ".stl");
 if (argc>2 && argv[2][0] != '-') sprintf(outfilename, "%s", argv[2]);
 else createFilename(infilename, "_fixed", outfilename, extension);

 if (skip_if_fixed && fopen(outfilename, "r")) TMesh::error("Output file already exists (-x option specified).");

 // The loader automatically reconstructs a manifold triangle connectivity
 if (tin.load(infilename) != 0) TMesh::error("Can't open file.\n");

 if (join_multiple_components)
 {
	 TMesh::info("\nJoining input components ...\n");
	 TMesh::begin_progress();
	 while (joinClosestComponents(&tin)) TMesh::report_progress("Num. components: %d       ", tin.shells());
	 TMesh::end_progress();
	 tin.deselectTriangles();
 }

	   // Keep only the largest component (i.e. with most triangles)
	   int sc = tin.removeSmallestComponents();
	   if (sc) TMesh::warning("Removed %d small components\n",sc);

	   // Fill holes
	   if (tin.boundaries())
	   {
		TMesh::warning("Patching holes\n");
		tin.fillSmallBoundaries(0, true);
	   }

	   // Run geometry correction
	   if (!tin.boundaries()) TMesh::warning("Fixing degeneracies and intersections...\n");
	   if (tin.boundaries() || !tin.meshclean()) TMesh::warning("MeshFix could not fix everything.\n", sc);


 TMesh::info("Saving output mesh ...\n");
 tin.save(outfilename);

 printf("Elapsed time: %d ms\n", clock() - beginning);

 return 0;

}

// Joins multiple open components
void Basic_TMesh_wrap::Join()
{
  TMesh::begin_progress();
  while (joinClosestComponents(this)) TMesh::report_progress("Num. components: %d       ", this->shells());
  TMesh::end_progress();
  this->deselectTriangles();
}

// Enables/disables console print out
void Basic_TMesh_wrap::SetVerbose(int quiet)
{
TMesh::quiet = quiet;
}


// Populate points array
void Basic_TMesh_wrap::PopArrays(double* points, int* faces)
{
  Node *n;
  Vertex *v;
  int c = 0;
  int i;
  coord *ocds;

  // Populate points
  FOREACHVERTEX(v, n)
  {
    points[c] = v->x;
    points[c + 1] = v->y;
    points[c + 2] = v->z;
    c += 3;
  }

  ocds = new coord[V.numels()];
  i=0; FOREACHVERTEX(v, n) ocds[i++] = v->x;
  i=0; FOREACHVERTEX(v, n) v->x = i++;

  // Populate faces
  c = 0;
  FOREACHNODE(T, n)
  {
    faces[c] = TVI1(n);
    faces[c + 1] = TVI2(n);
    faces[c + 2] = TVI3(n);
    c += 3;
  }

  // clean up
  i=0; FOREACHVERTEX(v, n) v->x = ocds[i++];
  delete[] ocds;

}


// Return the number of points in mesh
int Basic_TMesh_wrap::ReturnTotalPoints()
{
  return V.numels();
}


// Return the number of faces in mesh
int Basic_TMesh_wrap::ReturnTotalFaces()
{
  return T.numels();
}


// Loads arrays directly to TMesh object
int Basic_TMesh_wrap::loadArray(int nv, double *points, int nt, int *faces)
{
  Vertex *v;
  Node *n;
  int i;

  // Parse vertices
  for (i=0; i<nv; i++)
  {
    V.appendTail(newVertex(points[i*3], points[i*3 + 1], points[i*3 + 2]));
  }

  // Initialize triangle indexing array
  ExtVertex **var = (ExtVertex **)malloc(sizeof(ExtVertex *)*nv);
  i=0; FOREACHVERTEX(v, n) var[i++] = new ExtVertex(v);

  // Load triangles
  for (i=0; i<nt; i++)
  {
  CreateIndexedTriangle(var, faces[i*3], faces[i*3 + 1], faces[i*3 + 2]);
  }

  // Memory management
  for (i=0; i<nv; i++) delete(var[i]);
  free(var);
  
  TMesh::info("Loaded %d vertices and %d faces.\n", nv, nt);

  // Fix connectivity
  fixConnectivity();
  d_boundaries = d_handles = d_shells = 1;

  return 0;
}

// Adds indices of selected cells to external array
void Basic_TMesh_wrap::GetSelected(int *faces)
{
  Node *n;
  Triangle *t;

  int c = 0;
  int i = 0;
  FOREACHTRIANGLE(t, n) {
    if (IS_VISITED(t)){
      faces[i] = c;
      i++;
    }
  c++;
  }
}
