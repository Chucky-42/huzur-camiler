"""Weekly: rebuild the mosque tiles from OSM and push them if anything changed.

Run by the scheduled task HuzurCamilerHaftalik. A failed download or a
suspiciously small result leaves the published tiles untouched (build.py
refuses), so the app keeps serving last week's data rather than none.
"""
import datetime, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, 'yenile.log')
ENV = dict(os.environ, PYTHONIOENCODING='utf-8')


def log(msg):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write('%s %s\n' % (datetime.datetime.now().isoformat(timespec='seconds'), msg))


def run(*args):
    r = subprocess.run(args, cwd=HERE, env=ENV, capture_output=True, text=True,
                       encoding='utf-8', errors='replace')
    if r.returncode != 0:
        raise RuntimeError('%s -> %d\n%s\n%s' % (' '.join(args), r.returncode, r.stdout[-2000:], r.stderr[-2000:]))
    return r.stdout


def main():
    try:
        out = run(sys.executable, 'build.py')
        log('build ' + out.strip().splitlines()[-1])
        run('git', 'add', '-A', 'docs')
        if not run('git', 'status', '--porcelain', 'docs').strip():
            log('no change')
            return
        run('git', 'commit', '-qm', 'Weekly rebuild %s' % datetime.date.today().isoformat())
        run('git', 'push', '-q')
        log('pushed')
    except Exception as e:  # noqa: BLE001 - everything goes to the log
        log('FAILED ' + str(e).replace('\n', ' | ')[:3000])
        sys.exit(1)


if __name__ == '__main__':
    main()
