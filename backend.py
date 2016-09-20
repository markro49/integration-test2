import os, sys
import common
import argparse

def generate_graphs(project):
  #print "STARTED CLEANING PROJECT"
  #common.clean_project(project)
  #print "FINISHED CLEANING PROJECT"

  """Run dljc
  Compile test sources
  Generate program graphs using prog2dfg
  Precompute graph kernels that are independent of ontology stuff
  """
  print("Generating graphs for {0}".format(project))
  common.run_dljc(project,
                  ['graphtool'],
                  ['--graph-jar', common.get_jar('prog2dfg.jar')])

def gather_kernels(projects, corpus_kernel_file):
  print("Gathering kernels from projects {0}".format(" and ".join(projects)))
  corpus_kernel_file_handle = open(corpus_kernel_file, "w")
  for project in projects:
    project_dir = common.get_project_dir(project)
    project_kernel_file_path = common.get_kernel_path(project, out_dir)
    with open(project_kernel_file_path, "r") as fi: corpus_kernel_file_handle.write(fi.read())
  corpus_kernel_file_handle.close()

def generate_project_kernel(project, cluster_json=None):
  """ run graph kernel computation """
  
  project_dir = common.get_project_dir(project)

  out_dir = common.DOT_DIR[project]
  kernel_file_path = common.get_kernel_path(project, out_dir)
  
  if cluster_json:
    print("Using clustering output for node relabeling:")
    graph_kernel_cmd = ['python',
                        common.get_simprog('precompute_kernel.py'),
                        project_dir,
                        kernel_file_path,
                        cluster_json
                        ]
    output = common.run_cmd(graph_kernel_cmd)
    print(output)
  else:
    graph_kernel_cmd = ['python',
                        common.get_simprog('precompute_kernel.py'),
                        project_dir,
                        kernel_file_path
                        ]
    output = common.run_cmd(graph_kernel_cmd)
    print output
    
  print("Generated kernel file for {0} in {1}.".format(project, kernel_file_path))

def main():
  
  project_list = ["dyn4j", "jreactphysics3d", "jbox2d", "react", "jmonkeyengine"]

  parser = argparse.ArgumentParser()
  parser.add_argument("-c", "--cluster", type=str, help="path to the json file that contains clustering information")
  parser.add_argument("-g", "--graph", action="store_true", help="regenerate graphs from the programs")
  parser.add_argument("-d", "--dir", type=str, required=True, help="directory to store precomputed kernels")

  args = parser.parse_args()

  common.mkdir(args.dir)

  for project in project_list:
    if args.graph:
      generate_graphs(project)
    generate_project_kernel(project, args.cluster)

  # gather kernels for one-against-all comparisons
  for project in project_list:
    pl = list(project_list) # create a copy
    pl.remove(project)
    kernel_name = "kernel"
    gather_kernels(pl, os.path.join(common.WORKING_DIR, args.dir, project, "_", "kernel.txt"))

if __name__ == '__main__':
  main()
