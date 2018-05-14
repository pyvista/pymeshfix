#include "tmesh.h"
#include "meshfix.h"
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <stdio.h>

namespace T_MESH
{
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

// Joins multiple open components
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
		t->info = (void *)i;

		while (triList.numels())
		{
			t = (Triangle *)triList.popHead();
			if ((s = t->t1()) != NULL && s->info == NULL) { triList.appendHead(s); s->info = (void *)i; }
			if ((s = t->t2()) != NULL && s->info == NULL) { triList.appendHead(s); s->info = (void *)i; }
			if ((s = t->t3()) != NULL && s->info == NULL) { triList.appendHead(s); s->info = (void *)i; }
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

} // T_Mesh namespace
