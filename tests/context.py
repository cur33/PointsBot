"""Little path hack to allow tests to access the package. Import this in each
test script."""
import sys
from os.path import abspath, dirname, join
sys.path.insert(0, abspath(join(dirname(__file__), '..')))
