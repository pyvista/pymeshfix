#include "tmesh.h"
#include <stdlib.h>
#include <string.h>
#include <time.h>

//int MeshFix(const char*, int quiet, const char*);
//int MeshFix(int nv, double *points, int nt, int *faces, int quiet);


namespace T_MESH
{

// Adds additional functionality to original tetgen object
//class Basic_TMesh_wrap : public T_MESH::Basic_TMesh
class Basic_TMesh_wrap : public Basic_TMesh
{
    public:
        //constructor
        Basic_TMesh_wrap();

        // Enables/disables print outs
        void SetVerbose(int);

        // Loads arrays into Basic_TMesh object
        int loadArray(int, double *, int, int *);

        // Arrays out
        int ReturnTotalPoints();
        int ReturnTotalFaces();
        void PopArrays(double*, int*);

        void Join();

        //destructor
//        ~myRectangle();

};

};