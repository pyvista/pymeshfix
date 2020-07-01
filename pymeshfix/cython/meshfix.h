#include <stdlib.h>
#include <string.h>
#include <time.h>

#include "tmesh.h"
//#include "detectIntersections.h"


namespace T_MESH
{

// Adds additional functionality to original tetgen object
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

        // Used to select self-intersecting triangles
//        int selectIntersectingTriangles(UINT16, bool);
        void GetSelected(int *faces);

};

};
