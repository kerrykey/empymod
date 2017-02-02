import pytest
import numpy as np
from os.path import join, dirname
from numpy.testing import assert_allclose

# Import main modelling routines from empymod directly to ensure they are in
# the __init__.py-file.
from empymod import bipole, dipole, frequency, time
# Import rest from model
from empymod.model import gpr, wavenumber, fem, tem
from empymod.kernel import fullspace, halfspace

# These are kind of macro-tests, as they check the final results.
# I try to use different parameters for each test, to cover a wide range of
# possibilities. It won't be possible to check all the possibilities though.
# Add tests when issues arise!

# Load required data
# Data generated with create_empymod.py [27/01/2017]
DATAEMPYMOD = np.load(join(dirname(__file__), 'data_empymod.npz'))
# Data generated with create_fem_tem.py [27/01/2017]
DATAFEMTEM = np.load(join(dirname(__file__), 'data_fem_tem.npz'))
# Data generated with create_green3d.py [30/01/2017]
GREEN3D = np.load(join(dirname(__file__), 'data_green3d.npz'))
# Data generated with create_dipole1d.py [01/02/2017]
DIPOLE1D = np.load(join(dirname(__file__), 'data_dipole1d.npz'))
# Data generated with create_emmod.py [01/02/2017]
EMMOD = np.load(join(dirname(__file__), 'data_emmod.npz'))


class TestBipole:                                                   # 1. bipole
    def test_fullspace(self):                                   # 1.1 fullspace
        # Comparison to analytical fullspace solution
        fs = DATAEMPYMOD['fs'][()]
        fsbp = DATAEMPYMOD['fsbp'][()]
        for key in fs:
            # Get fullspace
            fs_res = fullspace(**fs[key])
            # Get bipole
            bip_res = bipole(**fsbp[key])
            # Check
            assert_allclose(fs_res, bip_res)

    def test_halfspace(self):                                   # 1.2 halfspace
        # Comparison to analytical fullspace solution
        hs = DATAEMPYMOD['hs'][()]
        hsbp = DATAEMPYMOD['hsbp'][()]
        for key in hs:
            # Get halfspace
            hs_res = halfspace(**hs[key])
            # Get bipole
            bip_res = bipole(**hsbp[key])
            # Check
            assert_allclose(hs_res, bip_res)

    def test_emmod(self):                            # 1.3. Comparison to EMmod
        # Comparsion to EMmod (Hunziker et al., 2015)
        # NOTE: The comparison to EMmod is with f=1.25Hz. It would be good to
        #       include further tests with much lower/higher frequencies!
        dat = EMMOD['res'][()]
        for key, val in dat.items():
            res = bipole(**val[0])
            assert_allclose(np.abs(res), np.abs(val[1]), 2e-2, 1e-20, True)
            assert_allclose(res, val[1], 3e-2, 1e-20, True)

    def test_dipole1d(self):                      # 1.4. Comparison to DIPOLE1D
        # Comparison to DIPOLE1D (Key, Scripps)
        def crec(rec, azm, dip):
            return [rec[0], rec[1], rec[2], azm, dip]

        def get_xyz(src, rec, depth, res, freq, srcpts):
            ex = bipole(src, crec(rec, 0, 0), depth, res, freq, srcpts=srcpts,
                        mrec=False, verb=0)
            ey = bipole(src, crec(rec, 90, 0), depth, res, freq, srcpts=srcpts,
                        mrec=False, verb=0)
            ez = bipole(src, crec(rec, 0, 90), depth, res, freq, srcpts=srcpts,
                        mrec=False, verb=0)
            mx = bipole(src, crec(rec, 0, 0), depth, res, freq, srcpts=srcpts,
                        mrec=True, verb=0)
            my = bipole(src, crec(rec, 90, 0), depth, res, freq, srcpts=srcpts,
                        mrec=True, verb=0)
            mz = bipole(src, crec(rec, 0, 90), depth, res, freq, srcpts=srcpts,
                        mrec=True, verb=0)
            return ex, ey, ez, mx, my, mz

        def comp_all(data, rtol=1e-3, atol=1e-24):
            inp, res = data
            Ex, Ey, Ez, Hx, Hy, Hz = get_xyz(**inp)
            assert_allclose(Ex, res[0], rtol, atol, True)
            assert_allclose(Ey, res[1], rtol, atol, True)
            assert_allclose(Ez, res[2], rtol, atol, True)
            assert_allclose(Hx, res[3], rtol, atol, True)
            assert_allclose(Hy, res[4], rtol, atol, True)
            assert_allclose(Hz, res[5], rtol, atol, True)

        # DIPOLES
        # 1. x-directed dipole
        comp_all(DIPOLE1D['xdirdip'][()])
        # 2. y-directed dipole
        comp_all(DIPOLE1D['ydirdip'][()])
        # 3. z-directed dipole
        comp_all(DIPOLE1D['zdirdip'][()])
        # 4. dipole in xy-plane
        comp_all(DIPOLE1D['xydirdip'][()])
        # 5. dipole in xz-plane
        comp_all(DIPOLE1D['xzdirdip'][()])
        # 6. dipole in yz-plane
        comp_all(DIPOLE1D['yzdirdip'][()])
        # 7. arbitrary xyz-dipole
        comp_all(DIPOLE1D['xyzdirdip'][()])

        # Bipoles
        # 8. x-directed bipole
        comp_all(DIPOLE1D['xdirbip'][()])
        # 9. y-directed bipole
        comp_all(DIPOLE1D['ydirbip'][()])
        # 10. z-directed bipole
        comp_all(DIPOLE1D['zdirbip'][()])
        # 11. bipole in xy-plane
        comp_all(DIPOLE1D['xydirbip'][()])
        # 12. bipole in xz-plane
        comp_all(DIPOLE1D['xzdirbip'][()])
        # 13. bipole in yz-plane
        comp_all(DIPOLE1D['yzdirbip'][()])
        # 14. arbitrary xyz-bipole
        comp_all(DIPOLE1D['xyzdirbip'][()])
        # 14.b Check bipole reciprocity
        inp, res = DIPOLE1D['xyzdirbip'][()]
        ex = bipole(crec(inp['rec'], 0, 0), inp['src'], inp['depth'],
                    inp['res'], inp['freq'], recpts=inp['srcpts'], verb=0)
        assert_allclose(ex, res[0], 2e-2, 1e-24, True)
        mx = bipole(crec(inp['rec'], 0, 0), inp['src'], inp['depth'],
                    inp['res'], inp['freq'], msrc=True, recpts=inp['srcpts'],
                    verb=0)
        assert_allclose(-mx, res[3], 2e-2, 1e-24, True)

    def test_green3d(self):                        # 1.5. Comparison to Green3D
        # Comparison to green3d (CEMI Consortium)
        def crec(rec, azm, dip):
            return [rec[0], rec[1], rec[2], azm, dip]

        def get_xyz(src, rec, depth, res, freq, aniso, strength, srcpts, msrc):
            ex = bipole(src, crec(rec, 0, 0), depth, res, freq, aniso=aniso,
                        msrc=msrc, mrec=False, strength=strength,
                        srcpts=srcpts, verb=0)
            ey = bipole(src, crec(rec, 90, 0), depth, res, freq, aniso=aniso,
                        msrc=msrc, mrec=False, strength=strength,
                        srcpts=srcpts, verb=0)
            ez = bipole(src, crec(rec, 0, 90), depth, res, freq, aniso=aniso,
                        msrc=msrc, mrec=False, strength=strength,
                        srcpts=srcpts, verb=0)
            mx = bipole(src, crec(rec, 0, 0), depth, res, freq, aniso=aniso,
                        msrc=msrc, mrec=True, strength=strength, srcpts=srcpts,
                        verb=0)
            my = bipole(src, crec(rec, 90, 0), depth, res, freq, aniso=aniso,
                        msrc=msrc, mrec=True, strength=strength, srcpts=srcpts,
                        verb=0)
            mz = bipole(src, crec(rec, 0, 90), depth, res, freq, aniso=aniso,
                        msrc=msrc, mrec=True, strength=strength, srcpts=srcpts,
                        verb=0)
            return ex, ey, ez, mx, my, mz

        def comp_all(data, rtol=1e-3, atol=1e-24):
            inp, res = data
            Ex, Ey, Ez, Hx, Hy, Hz = get_xyz(**inp)
            assert_allclose(Ex, res[0], rtol, atol, True)
            assert_allclose(Ey, res[1], rtol, atol, True)
            assert_allclose(Ez, res[2], rtol, atol, True)
            assert_allclose(Hx, res[3], rtol, atol, True)
            assert_allclose(Hy, res[4], rtol, atol, True)
            assert_allclose(Hz, res[5], rtol, atol, True)

        # ELECTRIC AND MAGNETIC DIPOLES
        # 1. x-directed electric and magnetic dipole
        comp_all(GREEN3D['xdirdip'][()])
        comp_all(GREEN3D['xdirdipm'][()])
        # 2. y-directed electric and magnetic dipole
        comp_all(GREEN3D['ydirdip'][()])
        comp_all(GREEN3D['ydirdipm'][()])
        # 3. z-directed electric and magnetic dipole
        comp_all(GREEN3D['zdirdip'][()], 5e-3)
        comp_all(GREEN3D['zdirdipm'][()], 5e-3)
        # 4. xy-directed electric and magnetic dipole
        comp_all(GREEN3D['xydirdip'][()])
        comp_all(GREEN3D['xydirdipm'][()])
        # 5. xz-directed electric and magnetic dipole
        comp_all(GREEN3D['xzdirdip'][()], 5e-3)
        comp_all(GREEN3D['xzdirdipm'][()], 5e-3)
        # 6. yz-directed electric and magnetic dipole
        comp_all(GREEN3D['yzdirdip'][()], 5e-3)
        comp_all(GREEN3D['yzdirdipm'][()], 5e-3)
        # 7. xyz-directed electric and magnetic dipole
        comp_all(GREEN3D['xyzdirdip'][()], 2e-2)
        comp_all(GREEN3D['xyzdirdipm'][()], 2e-2)
        # 7.b Check magnetic dipole reciprocity
        inp, res = GREEN3D['xyzdirdipm'][()]
        ey = bipole(crec(inp['rec'], 90, 0), inp['src'], inp['depth'],
                    inp['res'], inp['freq'], None, inp['aniso'],
                    mrec=inp['msrc'], msrc=False, strength=inp['strength'],
                    srcpts=1, recpts=inp['srcpts'], verb=0)
        assert_allclose(-ey, res[1], 2e-2, 1e-24, True)

        # ELECTRIC AND MAGNETIC BIPOLES
        # 8. x-directed electric and magnetic bipole
        comp_all(GREEN3D['xdirbip'][()], 5e-3)
        comp_all(GREEN3D['xdirbipm'][()], 5e-3)
        # 8.b Check electric bipole reciprocity
        inp, res = GREEN3D['xdirbip'][()]
        ex = bipole(crec(inp['rec'], 0, 0), inp['src'], inp['depth'],
                    inp['res'], inp['freq'], None, inp['aniso'],
                    mrec=inp['msrc'], msrc=False, strength=inp['strength'],
                    srcpts=1, recpts=inp['srcpts'], verb=0)
        assert_allclose(ex, res[0], 5e-3, 1e-24, True)
        # 9. y-directed electric and magnetic bipole
        comp_all(GREEN3D['ydirbip'][()], 5e-3)
        comp_all(GREEN3D['ydirbipm'][()], 5e-3)
        # 10. z-directed electric and magnetic bipole
        comp_all(GREEN3D['zdirbip'][()], 5e-3)
        comp_all(GREEN3D['zdirbipm'][()], 5e-3)

    def test_empymod_status_quo(self):                            # 1.6 empymod
        # Comparison to self, to ensure nothing changed.
        # 4 bipole-bipole cases in EE, ME, EM, MM, all different values
        for i in ['1', '2', '3', '4']:
            res = DATAEMPYMOD['out'+i][()]
            tEM = bipole(**res['inp'])
            assert_allclose(tEM, res['EM'])

    def test_empymod_dipole_bipole(self):
        # Compare a dipole to a bipole
        # Checking intpts, strength, reciprocity
        inp = {'depth': [0, 250], 'res': [1e20, 0.3, 5], 'freqtime': 1}
        rec = [8000, 200, 300, 0, 0]
        bip1 = bipole([-25, 25, -25, 25, 100, 170.7107], rec, srcpts=1,
                      strength=33, **inp)
        bip2 = bipole(rec, [-25, 25, -25, 25, 100, 170.7107], recpts=5,
                      strength=33, **inp)
        dip = bipole([0, 0, 135.3553, 45, 45], [8000, 200, 300, 0, 0], **inp)
        # r = 100; sI = 33 => 3300
        assert_allclose(bip1, dip*3300, 1e-5)  # bipole as dipole
        assert_allclose(bip2, dip*3300, 1e-2)  # bipole, src/rec switched.

    def test_empymod_optimizaton(self, capsys):
        # Compare optimization options: None, parallel, spline
        inp = {'depth': [0, 500], 'res': [10, 3, 50], 'freqtime': [1, 2, 3],
               'rec': [[6000, 7000, 8000], [200, 200, 200], 300, 0, 0],
               'src': [0, 0, 0, 0, 0]}

        non = bipole(opt=None, verb=3, **inp)
        out, _ = capsys.readouterr()
        assert "Hankel Opt.     :  None" in out

        par = bipole(opt='parallel', verb=3, **inp)
        out, _ = capsys.readouterr()
        assert "Hankel Opt.     :  Use parallel" in out
        assert_allclose(non, par, equal_nan=True)

        spl = bipole(opt='spline', verb=3, **inp)
        out, _ = capsys.readouterr()
        assert "Hankel Opt.     :  Use spline" in out
        assert_allclose(non, spl, 1e-3, 1e-22, True)

    def test_empymod_loop(self, capsys):
        # Compare loop options: None, 'off', 'freq'
        inp = {'depth': [0, 500], 'res': [10, 3, 50], 'freqtime': [1, 2, 3],
               'rec': [[6000, 7000, 8000], [200, 200, 200], 300, 0, 0],
               'src': [0, 0, 0, 0, 0]}

        non = bipole(loop=None, verb=3, **inp)
        out, _ = capsys.readouterr()
        assert "Loop over       :  None (all vectorized)" in out

        lpo = bipole(loop='off', verb=3, **inp)
        out, _ = capsys.readouterr()
        assert "Loop over       :  Offsets" in out
        assert_allclose(non, lpo, equal_nan=True)

        lfr = bipole(loop='freq', verb=3, **inp)
        out, _ = capsys.readouterr()
        assert "Loop over       :  Frequencies" in out
        assert_allclose(non, lfr, equal_nan=True)

    def test_empymod_fht_qwe(self, capsys):
        # Compare Hankel transforms
        inp = {'depth': [-20, 100], 'res': [1e20, 5, 100],
               'freqtime': [1.34, 23, 31], 'src': [0, 0, 0, 0, 90],
               'rec': [[200, 300, 400], [3000, 4000, 5000], 120, 90, 0]}

        fht = bipole(ht='fht', verb=3, **inp)
        out, _ = capsys.readouterr()
        assert "Hankel          :  Fast Hankel Transform" in out

        qwe = bipole(ht='qwe', verb=3, **inp)
        out, _ = capsys.readouterr()
        assert "Hankel          :  Quadrature-with-Extrapolation" in out
        assert_allclose(fht, qwe, equal_nan=True)

    def test_empymod_fft_qwe_fftlog(self, capsys):
        # Compare Fourier transforms
        inp = {'depth': [0, 300], 'res': [1e12, 1/3, 5],
               'freqtime': np.logspace(-1.5, 1, 20), 'signal': 0,
               'rec': [2000, 300, 280, 0, 0], 'src': [0, 0, 250, 0, 0]}

        ftl = bipole(ft='fftlog', verb=3, **inp)
        out, _ = capsys.readouterr()
        assert "Fourier         :  FFTLog" in out

        qwe = bipole(ft='qwe', verb=3, **inp)
        out, _ = capsys.readouterr()
        assert "Fourier         :  Quadrature-with-Extrapolation" in out
        assert_allclose(qwe, ftl, 1e-2, equal_nan=True)

        fft = bipole(ft='fft', verb=3, **inp)
        out, _ = capsys.readouterr()
        assert "Fourier         :  Sine-Filter" in out
        assert_allclose(fft, ftl, 1e-2, equal_nan=True)

    def test_empymod_example_wrong(self):
        # One example of wrong input. But inputs are checked in test_utils.py.
        with pytest.raises(ValueError):
            bipole([0, 0, 0], [0, 0, 0, 0, 0], [], 1, 1, verb=0)

    def test_empymod_combinations(self):
        # These are the 15 options that each bipole (src or rec) can take.
        # There are therefore 15x15 possibilities for src-rec combination
        # within bipole!
        # Here we are just checking a few possibilities... But these should
        # cover the principle and therefore hold for all cases.

        #                one_depth  dipole  asdipole one_bpdepth
        #   =====================================================
        #    .   .   .       TRUE     TRUE     TRUE     TRUE
        #   -----------------------------------------------------
        #    |   |   .       TRUE     TRUE     TRUE     TRUE
        #   -----------------------------------------------------
        #    |   |   |      false     TRUE     TRUE     TRUE
        #   -----------------------------------------------------
        #   . . . . . .      TRUE    false     TRUE     TRUE
        #                    TRUE    false    false     TRUE
        #                    TRUE    false     TRUE    false
        #                    TRUE    false    false    false
        #   -----------------------------------------------------
        #   | | | | . .      TRUE    false     TRUE     TRUE
        #                    TRUE    false    false     TRUE
        #                    TRUE    false     TRUE    false
        #                    TRUE    false    false    false
        #   -----------------------------------------------------
        #   | | | | | |     false    false     TRUE     TRUE
        #                   false    false    false     TRUE
        #                   false    false     TRUE    false
        #                   false    false    false    false
        #   -----------------------------------------------------

        inp = {'depth': [-100, 300], 'res': [1e20, 1, 10],
               'freqtime': [0.5, 0.9], 'src': [0, 0, 0, 0, 0]}

        # 1.1 three different dipoles
        da = bipole(rec=[7000, 500, 100, 0, 0], **inp)
        db = bipole(rec=[8000, 500, 200, 0, 0], **inp)
        dc = bipole(rec=[9000, 500, 300, 0, 0], **inp)

        # 1.2 three dipoles at same depth at once => comp to 1.1
        dd = bipole(rec=[[7000, 8000, 9000], [500, 500, 500], 100, 0, 0],
                    **inp)
        assert_allclose(dd[:, 0], da)

        # 1.3 three dipoles at different depths at once => comp to 1.1
        de = bipole(rec=[[7000, 8000, 9000], [500, 500, 500], [100, 200, 300],
                    0, 0], **inp)
        assert_allclose(de[:, 0], da)
        assert_allclose(de[:, 1], db)
        assert_allclose(de[:, 2], dc)

        # 2.1 three different bipoles
        # => asdipole/!asdipole/one_bpdepth/!one_bpdepth
        ba = bipole(rec=[7000, 7050, 100, 100, 2.5, 2.5], **inp)
        bb = bipole(rec=[7000, 7050, 100, 100, 2.5, 2.5], recpts=10, **inp)
        bc = bipole(rec=[7000, 7050, 100, 100, 0, 5], **inp)
        bd = bipole(rec=[7000, 7050, 100, 100, 0, 5], recpts=10, **inp)
        assert_allclose(ba, bb, 1e-3)
        assert_allclose(bc, bd, 1e-3)
        assert_allclose(ba, bc, 1e-2)  # As the dip is very small

        # 2.2 three bipoles at same depth at once
        # => asdipole/!asdipole/one_bpdepth/!one_bpdepth => comp to 2.1
        be = bipole(rec=[[7000, 8000, 9000], [7050, 8050, 9050],
                         [100, 100, 100], [100, 100, 100], 2.5, 2.5], **inp)
        bf = bipole(rec=[[7000, 8000, 9000], [7050, 8050, 9050],
                         [100, 100, 100], [100, 100, 100], 2.5, 2.5],
                    recpts=10, **inp)
        bg = bipole(rec=[[7000, 8000, 9000], [7050, 8050, 9050],
                    [100, 100, 100], [100, 100, 100], 0, 5], **inp)
        bh = bipole(rec=[[7000, 8000, 9000], [7050, 8050, 9050],
                         [100, 100, 100], [100, 100, 100], 0, 5], recpts=10,
                    **inp)
        assert_allclose(be[:, 0], ba)
        assert_allclose(bf[:, 0], bb)
        assert_allclose(bg[:, 0], bc)
        assert_allclose(bh[:, 0], bd)
        assert_allclose(be, bf, 1e-3)
        assert_allclose(bg, bh, 1e-3)
        assert_allclose(be, bg, 1e-2)  # As the dip is very small


def test_dipole():                                                  # 2. dipole
    # As this is a shortcut, just run one test to ensure
    # it is equivalent to bipole.
    src = [5000, 1000, -200]
    rec = [0, 0, 1200]
    model = {'depth': [100, 1000], 'res': [2, 0.3, 100], 'aniso': [2, .5, 2]}
    f = 0.01
    # v  dipole : ab = 26
    # \> bipole : src-dip = 90, rec-azimuth=90, msrc=True
    dip_res = dipole(src, rec, freqtime=f, ab=26, verb=0, **model)
    bip_res = bipole([src[0], src[1], src[2], 0, 90],
                     [rec[0], rec[1], rec[2], 90, 0], msrc=True, freqtime=f,
                     verb=0, **model)
    assert_allclose(dip_res, bip_res)


def test_gpr():                                                        # 3. gpr
    # empymod is not really designed for GPR, more work on the Hankel and
    # Fourier transform would be required for that; furthermore, you would
    # rather do that straight in the time domain. However, it works. We just
    # run a test here, to check that it remains the status quo.
    res = DATAEMPYMOD['gprout'][()]
    _, gprout = gpr(**res['inp'])
    assert_allclose(gprout, res['GPR'])


def test_wavenumber():                                          # 4. wavenumber
    # This is like `frequency`, without the Hankel transform. We just run a
    # test here, to check that it remains the status quo.
    res = DATAEMPYMOD['wout'][()]
    w_res0, w_res1 = wavenumber(**res['inp'])
    assert_allclose(w_res0, res['PJ0'])
    assert_allclose(w_res1, res['PJ1'])


def test_frequency():                                            # 5. frequency
    # As this is a shortcut, just run one test to ensure
    # it is equivalent to dipole with signal=None.
    src = [100, -100, 400]
    rec = [1000, 1000, 1000]
    model = {'depth': [0, 500], 'res': [1e12, 0.3, 10], 'aniso': [1, 1, 2]}
    f = 1
    ab = 45
    f_res = frequency(src, rec, freq=f, ab=ab, verb=0, **model)
    d_res = dipole(src, rec, freqtime=f, ab=ab, verb=0, **model)
    assert_allclose(f_res, d_res)


def test_time():                                                      # 6. time
    # As this is a shortcut, just run one test to ensure
    # it is equivalent to dipole with signal!=None.
    src = [-100, 300, 600]
    rec = [1000, -500, 400]
    model = {'depth': [-100, 600], 'res': [1e12, 3, 1], 'aniso': [1, 2, 3]}
    t = 10
    ab = 51
    signal = -1
    ft = 'fftlog'
    t_res = time(src, rec, time=t, signal=signal, ab=ab, ft=ft, verb=0,
                 **model)
    d_res = dipole(src, rec, freqtime=t, signal=signal, ab=ab, ft=ft,
                   verb=0, **model)
    assert_allclose(t_res, d_res)


def test_fem():                                                        # 7. fem
    # Just ensure functionality stays the same, with one example.
    for i in ['1', '2', '3', '4', '5']:
        res = DATAFEMTEM['out'+i][()]
        fEM, kcount, _ = fem(**res['inp'])
        assert_allclose(fEM, res['EM'])
        assert kcount == res['kcount']


def test_tem():                                                        # 8. tem
    # Just ensure functionality stays the same, with one example.
    for i in ['6', '7', '8']:  # Signal = 0, 1, -1
        res = DATAFEMTEM['out'+i][()]
        tEM, _ = tem(**res['inp'])
        assert_allclose(tEM, res['EM'])
