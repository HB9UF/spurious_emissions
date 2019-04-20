import numpy as np
from string import Template
import os

def process(prefix, counter, model, trace_2m, trace_70cm, f_2m = 145e6, f_70cm=431e6):
    trace_2m   = _process_trace(trace_2m)
    trace_70cm = _process_trace(trace_70cm)

    path = prefix + '/' + '%03d' % counter
    np.savetxt(path+'_2m.txt', trace_2m)
    np.savetxt(path+'_70cm.txt', trace_70cm)

    trace_2m = np.loadtxt(path+'_2m.txt')
    trace_70cm = np.loadtxt(path+'_70cm.txt')

    (dbm_2m, dbc_2m) = _extract_harmonics(trace_2m, f_2m, 5, 1e9)
    (dbm_70cm, dbc_70cm) = _extract_harmonics(trace_70cm, f_70cm, 4, 2e9)

    peak = ( (dbm_2m[0]+60)/10., (dbm_70cm[0]+60)/10.)

    tex = _generate_latex(model, prefix, '%03d' % counter, dbm_2m, dbc_2m, dbm_70cm, dbc_70cm, peak)
    fh = open(path + '.tex', 'w')
    fh.write(tex)
    fh.close()

    _render_and_print(prefix, '%03d' % counter)


def _process_trace(trace):
    dbm=np.array([float(i) for i in trace.rstrip('\n,').split(',')])
    f = np.linspace(0,15,len(dbm))
    return np.stack((f,(np.array(dbm)+60)/10)).transpose()

def _extract_harmonics(trace, fundamental, n_harmonics, end_freq):
    f = trace[:,0]
    dbm = trace[:,1]
    
    absolute = np.zeros( (n_harmonics) )
    relative = np.zeros( (n_harmonics) )

    for i in range(n_harmonics):
        freq = (i+1)*float(fundamental)
        val = freq/end_freq*15
        idx=np.abs(f-val).argmin()
        absolute[i] = dbm[idx]*10.-60
        relative[i] = absolute[i]-absolute[0]
    return (absolute, relative)


def _tex_checkmark(lim, dbc):
    if -lim > dbc:
        return '\\cmark'
    else:
        return '\\xmark'

def _get_limit(dbm):
    return 13+dbm

def _generate_latex(model, prefix, counter, dbm_2m, dbc_2m, dbm_70cm, dbc_70cm, peak):
    (lim_2m, lim_70cm) = (_get_limit(dbm_2m[0]), _get_limit(dbm_70cm[0]))
    fh = open('calibration_template.tex')
    source = Template(fh.read())
    fh.close()
    d = { 
            'model'  : model,
            'prefix' : prefix,
            'counter': counter,
            'abs_2m_0': round(dbm_2m[0],1),
            'abs_2m_1': round(dbm_2m[1],1),
            'abs_2m_2': round(dbm_2m[2],1), 
            'abs_2m_3': round(dbm_2m[3],1),
            'abs_2m_4': round(dbm_2m[4],1),
            'rel_2m_1': round(dbc_2m[1],1),
            'rel_2m_2': round(dbc_2m[2],1),
            'rel_2m_3': round(dbc_2m[3],1),
            'rel_2m_4': round(dbc_2m[4],1),
            'pf_2m_1' : _tex_checkmark(lim_2m, dbc_2m[1]),
            'pf_2m_2' : _tex_checkmark(lim_2m, dbc_2m[2]),
            'pf_2m_3' : _tex_checkmark(lim_2m, dbc_2m[3]),
            'pf_2m_4' : _tex_checkmark(lim_2m, dbc_2m[4]),
            'abs_70cm_0': round(dbm_70cm[0],1),
            'abs_70cm_1': round(dbm_70cm[1],1),
            'abs_70cm_2': round(dbm_70cm[2],1), 
            'abs_70cm_3': round(dbm_70cm[3],1),
            'rel_70cm_1': round(dbc_70cm[1],1),
            'rel_70cm_2': round(dbc_70cm[2],1),
            'rel_70cm_3': round(dbc_70cm[3],1),
            'pf_70cm_1' : _tex_checkmark(lim_70cm, dbc_70cm[1]),
            'pf_70cm_2' : _tex_checkmark(lim_70cm, dbc_70cm[2]),
            'pf_70cm_3' : _tex_checkmark(lim_70cm, dbc_70cm[3]),
            'peak_2m' : peak[0],
            'peak_70cm' : peak[1],
            'lim_2m' : peak[0] - lim_2m/10.,
            'lim_70cm' : peak[1] - lim_70cm/10.,
        }
    if dbm_2m[0] < 0:
        d['abs_2m_0'] = '-'
        d['abs_2m_1'] = '-'
        d['abs_2m_2'] = '-'
        d['abs_2m_3'] = '-'
        d['abs_2m_4'] = '-'
        d['rel_2m_1'] = '-'
        d['rel_2m_2'] = '-'
        d['rel_2m_3'] = '-'
        d['rel_2m_4'] = '-'
        d['pf_2m_1']  = '-'
        d['pf_2m_2']  = '-'
        d['pf_2m_3']  = '-'
        d['pf_2m_4']  = '-'
        d['peak_2m']  = 0
        d['lim_2m']   = 0
    if dbm_70cm[0] < 0:
        d['abs_70cm_0'] = '-'
        d['abs_70cm_1'] = '-'
        d['abs_70cm_2'] = '-'
        d['abs_70cm_3'] = '-'
        d['rel_70cm_1'] = '-'
        d['rel_70cm_2'] = '-'
        d['rel_70cm_3'] = '-'
        d['pf_70cm_1']  = '-'
        d['pf_70cm_2']  = '-'
        d['pf_70cm_3']  = '-'
        d['peak_70cm']  = 0
        d['lim_70cm']   = 0

    result = source.substitute(d)
    return result

def _render_and_print(prefix, counter):
    os.system('./render_latex.sh %s %s' % (prefix, counter))
    os.system('pdfjoin --outfile printjob.pdf %s/%s.pdf rueckseite.pdf' % (prefix, counter))
    os.system('lp -d hp_hp_LaserJet_1320_series printjob.pdf')
