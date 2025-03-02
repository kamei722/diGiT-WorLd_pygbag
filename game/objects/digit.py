import pygame
import time
import math

SEGMENT_MAP = {
    "0": {"A":1,"B":1,"C":1,"D":1,"E":1,"F":1,"G":0},
    "1": {"A":0,"B":1,"C":1,"D":0,"E":0,"F":0,"G":0},
    "2": {"A":1,"B":1,"C":0,"D":1,"E":1,"F":0,"G":1},
    "3": {"A":1,"B":1,"C":1,"D":1,"E":0,"F":0,"G":1},
    "4": {"A":0,"B":1,"C":1,"D":0,"E":0,"F":1,"G":1},
    "5": {"A":1,"B":0,"C":1,"D":1,"E":0,"F":1,"G":1},
    "6": {"A":1,"B":0,"C":1,"D":1,"E":1,"F":1,"G":1},
    "7": {"A":1,"B":1,"C":1,"D":0,"E":0,"F":0,"G":0},
    "8": {"A":1,"B":1,"C":1,"D":1,"E":1,"F":1,"G":1},
    "9": {"A":1,"B":1,"C":1,"D":1,"E":0,"F":1,"G":1},
    "A": {"A":1,"B":1,"C":1,"D":0,"E":1,"F":1,"G":1},
    "B": {"A":0,"B":0,"C":1,"D":1,"E":1,"F":1,"G":1},
    "C": {"A":1,"B":0,"C":0,"D":1,"E":1,"F":1,"G":0},
    "D": {"A":0,"B":1,"C":1,"D":1,"E":1,"F":0,"G":1},
    "E": {"A":1,"B":0,"C":0,"D":1,"E":1,"F":1,"G":1},
    "H": {"A":0,"B":1,"C":1,"D":0,"E":1,"F":1,"G":1},
    "I": {"A":0,"B":0,"C":0,"D":0,"E":1,"F":1,"G":0},
    "J": {"A":0,"B":1,"C":1,"D":1,"E":1,"F":0,"G":0},
    "L": {"A":0,"B":0,"C":0,"D":1,"E":1,"F":1,"G":0},
    "P": {"A":1,"B":1,"C":0,"D":0,"E":1,"F":1,"G":1},
    "N": {"A":0,"B":0,"C":1,"D":0,"E":1,"F":0,"G":1},
    "S": {"A":1,"B":0,"C":1,"D":1,"E":0,"F":1,"G":1},
    "U": {"A":0,"B":1,"C":1,"D":1,"E":1,"F":1,"G":0},
    "Y": {"A":0,"B":1,"C":1,"D":1,"E":0,"F":1,"G":1},
    "Z": {"A":1,"B":1,"C":0,"D":1,"E":1,"F":0,"G":1},
    "_": {"A":0,"B":0,"C":0,"D":1,"E":0,"F":0,"G":0},
    "¯": {"A":1,"B":0,"C":0,"D":0,"E":0,"F":0,"G":0},
    "T": {"A":1,"B":0,"C":0,"D":0,"E":0,"F":0,"G":0},
    "-": {"A":0,"B":0,"C":0,"D":0,"E":0,"F":0,"G":1},
    "M1": {"A":1,"B":1,"C":1,"D":0,"E":1,"F":1,"G":0},
    "N1": {"A":0,"B":1,"C":1,"D":0,"E":1,"F":1,"G":0},
    "G": {"A":1,"B":0,"C":1,"D":1,"E":1,"F":1,"G":0},
    "W": {"A":0,"B":1,"C":1,"D":1,"E":1,"F":1,"G":0},
    "G1": {"A":1,"B":0,"C":1,"D":1,"E":1,"F":1,"G":0},
    "K1": {"A":0,"B":0,"C":1,"D":0,"E":1,"F":1,"G":1},
    "R": {"A":0,"B":0,"C":0,"D":0,"E":1,"F":0,"G":1},
    "O": {"A":0,"B":0,"C":1,"D":1,"E":1,"F":0,"G":1},
    }
class DigitSegmentState:
    def __init__(self, transition_duration=0.8):
        self.phase = "off"
        self.active = False
        self.timer = 0.0
        self.alpha = 255
        self.transition_duration = transition_duration

class Digit:
    def __init__(self, x, y, width, height, number=None, properties_override=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = (255, 255, 255)

        self.segment_properties = {
            "A": {"one_way": True},
            "B": {"one_way": False},
            "C": {"one_way": False},
            "D": {"one_way": True},
            "E": {"one_way": False},
            "F": {"one_way": False},
            "G": {"one_way": True},
        }
        if properties_override:
            for key, override in properties_override.items():
                if key in self.segment_properties:
                    self.segment_properties[key].update(override)

        self.segments_state = {}
        for seg in self.segment_properties.keys():
            self.segments_state[seg] = DigitSegmentState()

        self.current_number = None
        self.next_number = number
        self.is_transitioning = False
        self.transition_start_time = time.time()

        self.active = True

        self.set_number(number)
        

    def get_segments_for_character(self, char):
        if char is None:
            return { seg:0 for seg in self.segment_properties.keys() }
        # SEGMENT_MAP から取得
        return SEGMENT_MAP.get(str(char).upper(),
                               { seg:0 for seg in self.segment_properties.keys() })

    def set_number(self, number):
        mapping = self.get_segments_for_character(number)
        for seg, st in self.segments_state.items():
            if mapping.get(seg,0) == 1:
                st.phase = "remain"
                st.active = True
                st.timer = 0.0
                st.alpha = 255
            else:
                st.phase = "off"
                st.active = False
                st.timer = 0.0
                st.alpha = 0
        self.current_number = number
        self.next_number = number

    def start_transition(self, new_number):
        old_map = self.get_segments_for_character(self.current_number)
        new_map = self.get_segments_for_character(new_number)
        for seg, st in self.segments_state.items():
            st.timer = 0.0
            old_on = old_map.get(seg,0)
            new_on = new_map.get(seg,0)
            if old_on==1 and new_on==1:
                st.phase = "remain"
                st.active = True
                st.alpha = 255
            elif old_on==1 and new_on==0:
                st.phase = "turning_off"
                st.active = True
                st.alpha = 255
            elif old_on==0 and new_on==1:
                st.phase = "turning_on"
                st.active = False
                st.alpha = 0
            else:
                st.phase = "off"
                st.active = False
                st.alpha = 0
        self.is_transitioning = True
        self.current_number = new_number
        self.transition_start_time = time.time()

    def update(self, dt):
        if not self.is_transitioning:
            return
        all_done = True
        for seg, st in self.segments_state.items():
            st.timer += dt
        for seg, st in self.segments_state.items():
            if st.phase=="remain":
                st.alpha=255
                st.active=True
            elif st.phase=="turning_off":
                if st.timer<st.transition_duration:
                    val=abs(math.sin(st.timer*10))
                    st.alpha=int(255*val)
                    st.active=True
                    all_done=False
                else:
                    st.phase="off"
                    st.alpha=0
                    st.active=False
            elif st.phase=="turning_on":
                if st.timer<st.transition_duration:
                    ratio=st.timer/st.transition_duration
                    st.alpha=int(255*ratio)
                    if ratio>0.5:
                        st.active=True
                    all_done=False
                else:
                    st.phase="remain"
                    st.alpha=255
                    st.active=True
            elif st.phase=="off":
                st.alpha=0
                st.active=False
        if all_done:
            self.is_transitioning=False
            #print("Digit transition completed")


    # A～G の矩形生成 (足場)
    def _get_segment_rects_AtoG(self):
        rects = {}
        thick_vert = int(self.width / 3.4)
        thick_horz = int(self.height / 10.3)

        rects["A"] = (
            pygame.Rect(
                int(self.x + self.width * 0.1),
                int(self.y),
                int(self.width - self.width * 0.2),
                thick_horz
            ), None
        )
        rects["B"] = (
            pygame.Rect(
                int(self.x + self.width - thick_vert),
                int(self.y + thick_horz),
                thick_vert,
                int(self.height / 2 - thick_horz + 1)
            ), None
        )
        rects["C"] = (
            pygame.Rect(
                int(self.x + self.width - thick_vert),
                int(self.y + self.height / 2 - 1),
                thick_vert,
                int(self.height / 2 - thick_horz + 1)
            ), None
        )

        # 隙間を埋めるための調整
        offset_D = 7 
        rects["D"] = (
            pygame.Rect(
                int(self.x + self.width * 0.1),
                int(self.y + self.height - thick_horz - offset_D),
                int(self.width - self.width * 0.2),
                thick_horz
            ), None
        )
        rects["E"] = (
            pygame.Rect(
                int(self.x),
                int(self.y + self.height / 2 - 1),
                thick_vert,
                int(self.height / 2 - thick_horz + 1)
            ), None
        )
        rects["F"] = (
            pygame.Rect(
                int(self.x),
                int(self.y + thick_horz),
                thick_vert,
                int(self.height / 2 - thick_horz + 1)
            ), None
        )
        rects["G"] = (
            pygame.Rect(
                int(self.x + self.width * 0.1),
                int(self.y + self.height / 2 - thick_horz / 2),
                int(self.width - self.width * 0.2),
                thick_horz
            ), None
        )

        return rects


    def get_platform_rects(self):
        """
        接触の隙間を埋めるためのオブジェクト一体化処理
        """

        if not self.active:
            return []

        result={}
        base_rects=self._get_segment_rects_AtoG()
        for seg,(rect,_) in base_rects.items():
            st=self.segments_state[seg]
            active = (st.active if st else False)
            result[seg] = (rect, active)

        groups=[]

        # ===== B,C 統合 =====
        b_rect, b_active = result.get("B",(None,False))
        c_rect, c_active = result.get("C",(None,False))
        if b_rect and c_rect and b_active and c_active:
            new_top = min(b_rect.top, c_rect.top)
            new_bottom = max(b_rect.bottom, c_rect.bottom)
            new_rect = pygame.Rect(b_rect.x, new_top, b_rect.width, new_bottom - new_top)
            one_way = self.segment_properties["B"]["one_way"]
            groups.append(("B+C", new_rect, one_way))
        else:
            if b_rect and b_active:
                one_way = self.segment_properties["B"]["one_way"]
                groups.append(("B", b_rect, one_way))
            if c_rect and c_active:
                one_way = self.segment_properties["C"]["one_way"]
                groups.append(("C", c_rect, one_way))

        # ===== E,F 統合 =====
        e_rect, e_active = result.get("E",(None,False))
        f_rect, f_active = result.get("F",(None,False))
        if e_rect and f_rect and e_active and f_active:
            new_top = min(e_rect.top, f_rect.top)
            new_bottom = max(e_rect.bottom, f_rect.bottom)
            # 幅は e_rect.width を用いるか f_rect.width を用いるか -> 同じ幅のはず
            new_rect = pygame.Rect(e_rect.x, new_top, e_rect.width, new_bottom - new_top)
            one_way = self.segment_properties["E"]["one_way"]
            groups.append(("E+F", new_rect, one_way))
        else:
            if e_rect and e_active:
                one_way = self.segment_properties["E"]["one_way"]
                groups.append(("E", e_rect, one_way))
            if f_rect and f_active:
                one_way = self.segment_properties["F"]["one_way"]
                groups.append(("F", f_rect, one_way))

        # ===== A,D,G =====
        for seg in ["A","D","G"]:
            if seg in result:
                rect, active = result[seg]
                if active and rect:
                    one_way=self.segment_properties[seg]["one_way"]
                    groups.append((seg, rect, one_way))

        return groups       

    def draw(self, screen, cam_x=0, cam_y=0):
        if not self.active:
            return

        # 最終ステージでのカメラオフセット
        cam_x = int(cam_x)
        cam_y = int(cam_y)

        base_rects = self._get_segment_rects_AtoG()

        if not hasattr(self, "segment_surfaces"):
            self.segment_surfaces = {}

        for seg in ["A", "B", "C", "D", "E", "F", "G"]:
            rect, _ = base_rects[seg]
            shifted_rect = pygame.Rect(
                int(rect.x - cam_x),
                int(rect.y - cam_y),
                int(rect.width),
                int(rect.height)
            )

            if seg == "D":
                shifted_rect.y -= 2

            st = self.segments_state[seg]
            if st.active and st.alpha > 0:
                # 状態が固定しているならキャッシュを利用
                if not self.is_transitioning:
                    if seg not in self.segment_surfaces:
                        surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                        pygame.draw.rect(surf, (*self.color, st.alpha), (0, 0, rect.width, rect.height))
                        self.segment_surfaces[seg] = surf
                    else:
                        surf = self.segment_surfaces[seg]
                else:
                    # トランジション中は毎フレーム新規生成
                    surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                    pygame.draw.rect(surf, (*self.color, st.alpha), (0, 0, rect.width, rect.height))
                screen.blit(surf, shifted_rect)
