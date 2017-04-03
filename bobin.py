import os, sys, re, math, collections


class BobinGraphDrawer(object):
    def __init__(self, graph):
        self.__graph = graph
        self.__angle = 0
        self.__size = 100
        self.__diameters = [150, 200, 350] # cluster inner, cluster outer, elements outer
        self.__curveture = 0.25#0.33#25
    def draw_elements(self, canvas):
        pass
    def draw_edges(self, canvas):
        pass

    def __draw_cluster_pdf(self, cluster, cnv, center, path, theta0, theta1, r, rmax):
        cx, cy = center
        if cluster.size <= 1: # leaf
            theta = (theta0 + theta1) * .5
            x0 = cx + r * math.cos(theta)
            y0 = cy + r * math.sin(theta)
            x1 = cx + rmax * math.cos(theta)
            y1 = cy + rmax * math.sin(theta)
            path.moveTo(x0, y0)
            path.lineTo(x1, y1)
        else:
            n0 = cluster.left.size
            n1 = cluster.right.size
            theta2 = theta0 + (theta1 - theta0) * n0 / (n0 + n1)
            dr = (rmax - r) / (cluster.depth + 1)
            tc1 = self.__draw_cluster_pdf(cluster.left, cnv, center, path, theta0, theta2, r + dr, rmax)
            tc2 = self.__draw_cluster_pdf(cluster.right, cnv, center, path, theta2, theta1, r + dr, rmax)
            ang = tc1
            tc3 = (tc1 + tc2) * .5
            x0 = cx - r - dr
            y0 = cy - r - dr
            x1 = cx + r + dr
            y1 = cy + r + dr
            path.arc(x0, y0, x1, y1, startAng=ang * 180 / math.pi, extent=(tc2 - tc1) * 180 / math.pi)
            path.moveTo(cx + r * math.cos(tc3), cy + r * math.sin(tc3))
            path.lineTo(cx + math.cos(tc3) * (r + dr), cy + math.sin(tc3) * (r + dr))
            theta = tc3
        return theta

    def draw_on_pdf(self, cnv):
        cluster = self.__graph.cluster_tree
        print(cluster)
        theta_per_elem = math.pi * 2 / cluster.size
        theta = self.__angle
        rmax = self.__diameters[1] * .5
        r = self.__diameters[0] * .5
        center = 300, 400
        path = cnv.beginPath()
        self.__draw_cluster_pdf(cluster, cnv, center, path, theta, theta + math.pi * 2, r, rmax)
        t = theta + math.pi * 2 / cluster.size * .5
        dt = math.pi * 2 / cluster.size
        r_elem = self.__diameters[1] * .5
        cnv.saveState()
        cnv.setLineCap(2)
        cnv.drawPath(path)
        item2index = []
        for elem in cluster.nodes:
            x0 = center[0] + r_elem * math.cos(t)
            y0 = center[1] + r_elem * math.sin(t)
            cnv.translate(x0, y0)
            cnv.rotate(t * 180 / math.pi)
            cnv.drawString(0, 0, elem.name)
            cnv.resetTransforms()
            i2i = {}
            for i, item in enumerate(self.__graph.get_items(elem.name)):
                i2i[item] = i
            item2index.append(i2i)
            t += dt
        dia1 = self.__diameters[1]
        dia2 = self.__diameters[2]
        cx, cy = center
        curve_coeff = self.__curveture
        def __get_color(i, j):
            if abs(i - j) == 1:
                return 'red'
            return 'navy'
        for i in range(cluster.size):
            theta1 = self.__angle + (i + .5) * math.pi * 2 / cluster.size
            itemlist1 = item2index[i]
            num1 = len(itemlist1)
            cos1 = math.cos(theta1) * curve_coeff
            sin1 = math.sin(theta1) * curve_coeff

            for j in range(i+1, cluster.size):
                theta2 = self.__angle + (j + .5)  * math.pi * 2 / cluster.size
                cos2 =- math.cos(theta2) * curve_coeff
                sin2 =- math.sin(theta2) * curve_coeff
                dt = theta2 - theta1
                path = cnv.beginPath()
                while dt > math.pi: dt -= math.pi * 2
                while dt < -math.pi: dt += math.pi * 2
#                print('{},{}\t{}\t{:.2f}\t{:.2f}\t{:.2f}'.format(i, j, dt > 0, dt, theta1, theta2))
                if abs(i - j) % 2 == 1 or (j == cluster.size - 1 and i == j - 1):#dt > 0:
                    cos1, sin1 = -cos1, -sin1
                    cos2, sin2 = -cos2, -sin2
                else:
                    cos1, sin1 = -cos1, -sin1
#                else:
#                    if theta1 > theta2:


                itemlist2 = item2index[j]
                num2 = len(itemlist2)
                accepted = 0
                #print(itemlist1, itemlist2)
                for item1, i1 in itemlist1.items():
                    if item1 in itemlist2:
                        i2 = itemlist2[item1]
                        rad1 = ((dia2 - dia1) * i1 / num1 + dia1) * .5
                        rad2 = ((dia2 - dia1) * i2 / num2 + dia1) * .5
                        x1 = cx + rad1 * math.cos(theta1)
                        y1 = cy + rad1 * math.sin(theta1)
                        x2 = cx + rad2 * math.cos(theta2)
                        y2 = cy + rad2 * math.sin(theta2)
                        dist = math.sqrt((x1 - x2)** 2 + (y1 - y2) ** 2)

                        x3 = x1 + dist * sin1
                        y3 = y1 - dist * cos1

                        x4 = x2 + dist * sin2
                        y4 = y2 - dist * cos2

                        path.moveTo(x1, y1)
                        path.curveTo(x3, y3, x4, y4, x2, y2)
                        accepted += 1
                print(i, j, accepted, __get_color(i, j))
                        #print(x1, y1, x2, y2, x3, y3, x4, y4)
                cnv.setLineWidth(1)#0.1)
                #print(i, j, __get_color(i,j))
                cnv.setStrokeColor(__get_color(i, j))
                cnv.drawPath(path)
        cnv.restoreState()



class BobinGraph(object):
    class node(object):
        def __init__(self):
            pass
        def __error_abstract(self):
            raise Exception('not implemented in abstract class')
        def __repr__(self):
            return self.name
        size = property(__error_abstract)
        name = property(__error_abstract)
        nodes = property(__error_abstract)
        depth = property(__error_abstract)
    class leaf(node):
        def __init__(self, label):
            self.__name = re.sub('[;\\(\\)]', '_', label)
        size = property(lambda s:1)
        name = property(lambda s: s.__name)
        depth = property(lambda s:0)
    class branch(node):
        def __init__(self, left, right):
            self.left = left
            self.right = right
            self.__size = left.size + right.size
            self.__depth = max(left.depth, right.depth) + 1
        def __enumerate_leaves(self):
            for obj in self.left, self.right:
                if obj.size == 1:
                    yield obj
                else:
                    for leaf in obj.__enumerate_leaves():
                        yield leaf
        size = property(lambda s:s.__size)#left.size + s.right.size)
        name = property(lambda self:'({};{})'.format(self.left.name, self.right.name))
        nodes = property(__enumerate_leaves)
        depth = property(lambda self:self.__depth)
    def __init__(self, name):
        self.__cluster = None
        self.__elements = None
        self.__total_number = 20000
        self.__elements = collections.OrderedDict()
        self.__matrix = None
    def get_items(self, label):
        return self.__elements[label]
    def add_element(self, name, itemlist):
        self.__elements[name] = set(itemlist)
        self.__cluster = None
    def __get_total(self):
        return self.__total_number
    def __set_total(self, num):
        for e in self.__elements.values():
            if len(e) > num:
                raise Exception('less than the number in given object list')
        self.__total_number = num
        self.__cluster = None
    def __get_cluster(self):
        self.__cluster_elements()
        return self.__cluster
    N = property(__get_total, __set_total)
    cluster_tree = property(__get_cluster)
    def __cluster_elements(self, distance_evaluator=None):
        if self.__cluster: return
        num = len(self.__elements)
        matrix = [[0] * num for i in range(num)]
        if distance_evaluator is None:
            distance_evaluator = self.__phicorrelation
        items = self.__elements.values()
        for i in range(num):
            items_i = items[i]
            for j in range(i):
                items_j = items[j]
                n00 = n01 = n10 = n11 = 0
                for g in items_i:
                    if g in items_j:
                        n11 += 1
                    else:
                        n01 += 1
                n10 = len(items_j) - n11
                n00 = self.__total_number - (n01 + n10 + n11)
                matrix[i][j] = matrix[j][i] = distance_evaluator(n00, n01, n10, n11)
        # clustering
        nodes = [BobinGraph.leaf(n_) for n_ in self.__elements.keys()]
        for loop in range(num - 1):
            N = len(nodes)
            maxcor = -10000.0
            maxpair = None, None
            for i in range(N):
                row = matrix[i]
                if row is None: continue
                for j in range(i):
                    cor = row[j]
                    if cor is None: continue
                    if cor > maxcor:
                        maxcor = cor
                        maxpair = i, j
            b, a = maxpair
            print(loop, a, b, maxcor)
            nodes[a] = BobinGraph.branch(nodes[a], nodes[b])
            nodes[b] = None
            for i in range(N):
                num = 0
                s = matrix[a][i]
                t = matrix[b][i]
                if s is not None and t is not None:
                    matrix[a][i] = matrix[i][a] = (s + t) * .5
                if matrix[i] is not None: matrix[i][b] = None
            matrix[b] = None
        self.__cluster = nodes[0]

    @staticmethod
    def __phicorrelation(n00, n01, n10, n11):
        n0_ = n00 + n01
        n1_ = n10 + n11
        n_0 = n00 + n10
        n_1 = n01 + n11
        a = n00 * n11
        b = n01 * n10
        if n0_ == 0 or n1_ == 0 or n_0 == 0 or n_1 == 0:
            if a == b:
                return 1.0
            elif a > b:
                return float('inf')
            elif a < b:
                return float('-inf')
        else:
            return (a - b) / math.sqrt(n0_ * n1_ * n_0 * n_1)

if __name__ == '__main__':
    import random
    b = BobinGraph('test')
    b.N = 100
    for i in range(6):
        genes = []
        for j in range(100):
            if random.randint(0, 10) == 0:
                genes.append('{}'.format(j))#ABCDEFGHIJKLMNOPQRSTUVWXYZ'[j])
        print(i, genes)
        b.add_element('Leaf{}'.format(i + 1), genes)
    b.add_element('Dummy', genes)
    print(b.cluster_tree)
    for leaf in b.cluster_tree.nodes:
        print(leaf)
    graph = BobinGraphDrawer(b)
    import reportlab.pdfgen.canvas
    cnv = reportlab.pdfgen.canvas.Canvas('test.pdf')
    graph.draw_on_pdf(cnv)
    cnv.save()
