class Neighbours:
    def __init__(self):
        pass

    @staticmethod
    def is_point_on_segment(p, q, r):
        return (max(p[0], r[0]) >= q[0] >= min(p[0], r[0]) and
                q[1] <= max(p[1], r[1]) and q[1] >= min(p[1], r[1]))

    @staticmethod
    def orientation(p, q, r):
        val = (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])
        if val == 0:
            return 0
        return 1 if val > 0 else 2

    def do_segments_intersect(self, p1, q1, p2, q2):
        o1 = self.orientation(p1, q1, p2)
        o2 = self.orientation(p1, q1, q2)
        o3 = self.orientation(p2, q2, p1)
        o4 = self.orientation(p2, q2, q1)

        if o1 != o2 and o3 != o4:
            return True

        if o1 == 0 and self.is_point_on_segment(p1, p2, q1):
            return True
        if o2 == 0 and self.is_point_on_segment(p1, q2, q1):
            return True
        if o3 == 0 and self.is_point_on_segment(p2, p1, q2):
            return True
        if o4 == 0 and self.is_point_on_segment(p2, q1, q2):
            return True

        return False

    def do_segments_share_an_edge(self, room1_coords, room2_coords):
        for i in range(len(room1_coords)):
            p1, q1 = room1_coords[i], room1_coords[(i + 1) % len(room1_coords)]
            for j in range(len(room2_coords)):
                p2, q2 = room2_coords[j], room2_coords[(j + 1) % len(room2_coords)]
                if self.do_segments_intersect(p1, q1, p2, q2):
                    return True
        return False

    def do_rooms_share_a_vertex(self, room1_coords, room2_coords):
        for coord1 in room1_coords:
            if coord1 in room2_coords:
                return True
        return False

    def are_rooms_neighbors(self, room1_coords, room2_coords):
        if self.do_segments_share_an_edge(room1_coords, room2_coords):
            return True
        if self.do_rooms_share_a_vertex(room1_coords, room2_coords):
            return True
        return False