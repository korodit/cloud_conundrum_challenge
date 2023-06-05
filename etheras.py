from os import listdir
import pprint

print_on = False

class DependencyGraph:
    # Duplication of information exists - maybe all info could get into one dictionary?
    def __init__(self,dir):
        self.nodes = {}
        self.parse_stack_files(dir)
        self.topological_list = []
        self.node_position = {}
        self.order_deps()

    def parse_stack_files(self,dir):
        filelist = [f for f in listdir(dir)]
        # print(*sorted(filelist),sep="\n")
        for file in filelist:
            if not file in self.nodes:
                self.nodes[file] = []
            with open(dir+"/"+file,"r") as stackfile:
                dependencies = list(map(lambda x:x.strip(),stackfile.readlines()))
                for dep in dependencies:
                    if not dep in self.nodes:
                        self.nodes[dep] = []
                self.nodes[file] = dependencies
    
    # Breadth first search, with env stack as starting nodes
    def missing_dependencies(self,env):
        front = env.copy()
        usedset = set(front)
        while(front!=[]):
            newfront = []
            for stack in front:
                for dep in self.nodes[stack]:
                    if not dep in usedset:
                        newfront.append(dep)
                        usedset.add(dep)
            front = newfront
        
        envset = set(env)
        newdeps = list(usedset.difference(envset))
        return newdeps

    # DAG Topological ordering
    # Could use Queue for better performance
    def order_deps(self):
        temporary_nodes = {}
        reverse_nodes = {}

        for node in self.nodes:
            if not node in temporary_nodes:
                temporary_nodes[node] = set(self.nodes[node])
            if not node in reverse_nodes:
                reverse_nodes[node] = []

        S = []
        L = []

        for node in self.nodes:
            for dep in self.nodes[node]:
                reverse_nodes[dep].append(node)
            if self.nodes[node] == []:
                S.append(node)
        if print_on:
            print("\n")
            pprint.pprint(temporary_nodes)
            print("\n")
            pprint.pprint(reverse_nodes)

        if S == []:
            print("The graph is NOT a DAG! Exiting.")
            exit(1)
        
        while S != []:
            curr_node = S.pop(0)
            L.append(curr_node)
            for connection in reverse_nodes[curr_node]:
                temporary_nodes[connection].remove(curr_node)
                if not temporary_nodes[connection]:
                    S.append(connection)
        self.topological_list = L
        for i in range(len(self.topological_list)):
            self.node_position[self.topological_list[i]] = i

    # Returns a valid build order for the given stacks
    def build_order(self,envlist):
        return sorted(envlist,key=lambda stack:self.node_position[stack])

    # Return a tuple.
    # First element is True/False, based on whether the environment stacks
    # are valid or not, separately. Then, return a list of missing dependencies
    # based on the provided stacks, if needed.
    def validate_verify_envlist(self,envlist):
        for stack in envlist:
            if stack not in self.nodes:
                return (False,[])
        
        return (True,self.missing_dependencies(envlist))

    def show_topo(self):
        print("\nShowing ordered topology of the graph:")
        print(self.topological_list)
        print(self.node_position)

    def show_nodes(self):
        print("\nPrinting graph nodes and edges")
        pprint.pprint(self.nodes)

class Environment:
    def __init__(self,envlist=[],missing=[],build_order=[],valid=True):
        self.envlist = envlist
        self.missing = missing
        self.build_order = build_order
        self.valid = valid
    def __str__(self):
        return str([self.envlist,self.missing,self.build_order,"VALID" if self.valid else "INVALID"])
    def __repr__(self):
        return pprint.pformat([self.envlist,self.missing,self.build_order,"VALID" if self.valid else "INVALID"],indent=4)

class Environments:
    def __init__(self,envdir,dagdir):
        self.dag = DependencyGraph(dagdir)
        self.envs = {}
        self.parse_env_files(envdir)

    def parse_env_files(self,dir):
        filelist = [f for f in listdir(dir)]
        for file in filelist:
            with open(dir+"/"+file,"r") as envfile:
                stacks = list(map(lambda x:x.strip(),envfile.readlines()))
                if print_on:
                    print("Printing environment stacks:")
                    print(stacks)
                (valid,missing) = self.dag.validate_verify_envlist(stacks)
                build_order = []
                if valid:
                    build_order = self.dag.build_order(stacks+missing)
                self.envs[file] = Environment(stacks,missing,build_order,valid)
    
    def show_envs(self):
        print("\nPrinting Parsed Environments [Starting stacks][Missing stacks][Build Order][Validity]")
        pprint.pprint(self.envs)

if __name__=="__main__":
    envs = Environments("environments","stacks")
    envs.dag.show_nodes()
    envs.dag.show_topo()
    envs.show_envs()