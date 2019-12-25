#!/usr/bin/env python
import sys
import os


if __name__=='__main__':
	#1. run prepare_map.py
	if len(sys.argv) < 2:
		print ('specify mapfile')
		exit(-1)
	mapfile = sys.argv[1]
	mapfile_dir,mapfile_name = os.path.split(mapfile)
	tmp_dirname = 'tmp'
	script_path = os.path.realpath(__file__)
	script_dirname,_ = os.path.split(script_path)
	if not os.path.exists(tmp_dirname):
		os.makedirs(tmp_dirname)
	prepare_script = 'prepare_map.py'
	prepare_script = os.path.join(script_dirname,prepare_script)
	tmp_mapfile = os.path.join(tmp_dirname,mapfile_name)
	tmp_datafile = os.path.join(tmp_dirname,mapfile_name+'.dat')
	print ('Params OK')
	print ('Preparing map...')
	os.system("python %s %s %s %s" % (prepare_script,mapfile,tmp_mapfile,tmp_datafile))
	print ('Map prepared')
	print ('Prepared mapfile and .dat file saved to %s'%tmp_dirname)

	#2. run check_for_mistakes.py
	check_script = 'check_for_mistakes.py'
	check_script = os.path.join(script_dirname,check_script)
	print ('Running check map script')
	print ('Save data before close (just press "s")')
	os.system("python %s %s %s" % (check_script,tmp_mapfile,tmp_datafile))
	print ('Check finished')

	#3. run top_routes.p
	print ('Fill params for find top routes:')
	start = input('Start point: ')
	finish = input('Finish point: ')
	kps_in = input('kps in search (ex. 3,5,7-9,13): ')
	mashtab = input('Mashtab: ')
	kps_to_skip = input('Сколько КП можно пропустить: ')
	top_routes_script = 'top_routes.py'
	top_routes_script = os.path.join(script_dirname,top_routes_script)
	output_dirname = os.path.join(mapfile_dir,os.path.splitext(mapfile_name)[0])
	if not os.path.exists(output_dirname):
		os.makedirs(output_dirname)
	print ('Running top routes scirpt')
	command = 'python %s -m %s -s %s -f %s --kps-in %s -d %s --mashtab %s -o %s --kps-to-skip %s' % \
				(top_routes_script,mapfile,start,finish,kps_in,tmp_datafile,mashtab,output_dirname,kps_to_skip)
	print (command)
	os.system(command)
	print ('Done')







