# encoding=utf-8

import os
import shutil
import time
import argparse
import sys

APP_VERSION_PREFIX: str = "v2.9.6-dev-"

def do_clean():
	print("一些清理工作...")
	if os.path.exists("testdata"):
		shutil.rmtree("testdata")

def update_version():
	print("更新版本号...")
	version = APP_VERSION_PREFIX + time.strftime("%Y.%m.%d")
	print("版本号:", version)
	with open("config/version.txt", "w+") as fp:
		fp.write(version + "\n")


def check_and_install_pkg(py_module, pip_version = ""):
	try:
		__import__(py_module)
	except ImportError:
		print("准备安装:", pip_version)
		cmd = sys.executable
		os.system("%s -m pip install \"%s\"" % (cmd, pip_version))

def py_exec(cmd_line):
	os.system("%s %s" % (sys.executable, cmd_line))

def run_test(args):
	target = args.target
	if args.test_mysql:
		args.skip_mysql_test = False
	os.environ["skip_mysql_test"] = str(args.skip_mysql_test)
	os.environ["mysql_host"] = str(args.mysql_host)
	os.environ["mysql_password"] = str(args.mysql_password)
	os.environ["mysql_database"] = str(args.mysql_database)
	os.environ["mysql_user"] = str(args.mysql_user)

	if target == "xutils":
		py_exec("-m pytest tests/test_xutils.py --doctest-modules --cov xutils --capture no")
		py_exec("-m coverage html -i")
		return
	
	if target == "xutils_db":
		# py_exec("-m pytest tests/test_xutils_db.py::TestMain::test_dbutil_mysql_enhanced --doctest-modules --cov xutils.db --cov handlers.system.db_index --capture no")
		py_exec("-m pytest tests/test_xutils_db.py tests/test_xutils_db_table.py tests/test_xutils_db_hash_table.py \
	  			--doctest-modules --cov xutils.db --cov handlers.system.db_index --cov xutils.db2 --capture no")
		py_exec("-m coverage html -i")
		return
	
	if target == "xutils_sqldb":
		py_exec("-m pytest tests/test_xutils_sqldb.py --doctest-modules --cov xutils.sqldb --cov handlers.system.db_index \
	  			--capture no")
		py_exec("-m coverage html -i")
		return
	
	if target == "xutils_cache":
		py_exec("-m pytest tests/test_xutils_cache.py --doctest-modules --cov xutils.cacheutil --capture no")
		py_exec("-m coverage html -i")
		return

	if target == "fs":
		py_exec("-m pytest tests/test_fs.py --doctest-modules --cov handlers.fs --cov handlers.fs --capture no")
		py_exec("-m coverage html -i")
		return

	if target == "app":
		py_exec("-m pytest tests/test_app.py --doctest-modules --cov handlers --capture no")
		py_exec("-m coverage html -i")
		return
	
	if target == "note":
		py_exec("-m pytest tests/test_note.py --doctest-modules --cov handlers --capture no")
		py_exec("-m coverage html -i")
		return
	
	if target == "system_sync":
		py_exec("-m pytest tests/test_system_sync.py --doctest-modules --cov handlers.system.system_sync --capture no")
		py_exec("-m coverage html -i")
		return
	
	if target == "message":
		py_exec("-m pytest tests/test_message.py --doctest-modules --cov handlers.message --capture no")
		py_exec("-m coverage html -i")
		return
	
	if target == "xauth":
		py_exec("-m pytest tests/test_xauth.py --doctest-modules --cov xauth --capture no")
		py_exec("-m coverage html -i")
		return

	if target == "admin":
		py_exec("-m pytest tests/test_admin.py --doctest-modules --cov handlers --capture no")
		py_exec("-m coverage html -i")
		return
	
	if target == "service":
		py_exec("-m pytest tests/test_service.py --doctest-modules --cov xnote.service --capture no")
		py_exec("-m coverage html -i")
		return

	if target != "all":
		print("未知的操作:", target)
		sys.exit(1)
	
	executable = sys.executable
	check_and_install_pkg("pytest", "pytest>=5.1.0")
	check_and_install_pkg("pytest_cov", "pytest-cov>=2.7.1")
	check_and_install_pkg("coveralls", "python-coveralls>=2.9.3")
	check_and_install_pkg("coverage", "coverage==4.5.4")
	check_and_install_pkg("bs4", "beautifulsoup4==4.12.2")
	check_and_install_pkg("pymysql", "PyMySQL==1.0.2")
	check_and_install_pkg("lmdb", "lmdb==1.4.1")
	if os.name != "nt":
		check_and_install_pkg("leveldb", "leveldb==0.201")
	os.system("%s -m pytest tests --doctest-modules --cov handlers --cov xutils --cov core --cov xnote --ff" % executable)
	os.system(f"{executable} -m coverage html -i")

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("target", default="all", nargs="?")
	parser.add_argument("--run_mysql_test", default="true")
	parser.add_argument("--test_mysql", action="store_true", default=False)
	parser.add_argument("--mysql_host", default="192.168.50.96")
	parser.add_argument("--mysql_user", default="test")
	parser.add_argument("--mysql_password", default="gR4!KTO@9q")
	parser.add_argument("--mysql_database", default="test")
	args = parser.parse_args()

	args.skip_mysql_test = (args.run_mysql_test.lower() == "false")
	print(f"option: run_mysql_test={args.run_mysql_test}")

	do_clean()

	update_version()

	run_test(args)

	# do_clean()

if __name__ == '__main__':
	main()
