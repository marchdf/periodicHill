Periodic Hill
=============

This repository contains the case files for running the periodic hill
turbulence test case. This test case is based on the `ERCOFTAC UFR
3-30 Test Case
<http://qnet-ercoftac.cfms.org.uk/w/index.php/UFR_3-30_Test_Case>`_. The
Reynolds number (based on the hill height) is 10600. The hill height
is 1 m. The fluid density is set to :math:`1 \unitfrac{kg}{m^3}`. The
fluid bulk velocity is :math:`1 \unitfrac{m}{s}`. The viscosity is
therefore :math:`\nicefrac{1}{10600}`. The boundary conditions are
periodic in the streamwise and the spanwise directions. The bottom and
top boundary conditions are walls. A fixed forcing is applied at
:math:`\nicefrac{y}{h} > 1` to ensure a unity bulk velocity at
:math:`\nicefrac{x}{h} = 0`.
