// wmake capability smoke test for T12 custom-BC development
#include "fvCFD.H"
#include "volFields.H"
namespace Foam { namespace t12 {
    // representative of the coverage closure evaluation Theta(j,v,theta)
    scalar coverageVogt(const scalar j) { return 0.023*Foam::pow(max(j,SMALL), 0.3); }
}}
