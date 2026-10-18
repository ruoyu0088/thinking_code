from z3 import Int, Solver, Or, And, sat

def color_graph_using_Z3(G, total, limit):
    colors=[Int('colors_%d' % p) for p in range(total)]

    s=Solver()

    for i in G:
        s.add(colors[i[0]]!=colors[i[1]])

    # limit:
    for i in range(total):
        s.add(And(colors[i]>=0, colors[i]<limit))

    assert s.check()==sat
    m=s.model()
    # get solution and return it:
    return [m[colors[p]].as_long() for p in range(total)]



def block_model(s):
    m = s.model()
    s.add(Or([ f() != m[f] for f in m.decls() if f.arity() == 0]))    


def all_solutions(solver):
    while sat == solver.check():
        yield solver.model()
        block_model(solver)
        
        
def all_smt(s, initial_terms):
    def block_term(s, m, t):
        s.add(t != m.eval(t))
    def fix_term(s, m, t):
        s.add(t == m.eval(t))
    def all_smt_rec(terms):
        if sat == s.check():
            m = s.model()
            yield m
            for i in range(len(terms)):
                s.push()
                block_term(s, m, terms[i])
                for j in range(i):
                    fix_term(s, m, terms[j])
                yield from all_smt_rec(terms[i:])
                s.pop()   
    yield from all_smt_rec(list(initial_terms))