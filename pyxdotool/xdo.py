import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable, Optional, Union, cast

import Xlib
import Xlib.display

MAX_TRIES = 500


class XdoError(RuntimeError):
    pass


class XdoSearchDirection(Enum):
    PARENTS = 1
    CHILDREN = 2


@dataclass
class XdoScreenInfo:
    num: int
    x: int
    y: int
    width: int
    height: int


class Xdo:
    def __init__(self, display_name: Optional[str] = None) -> None:
        self.xdpy = Xlib.display.Display()
        if not self.xdpy:
            raise XdoError(f"Error: Can't open display: {display_name}")
        self.root = self.xdpy.screen().root

    def _ewmh_is_supported(self, feature: str) -> bool:
        request = self.xdpy.intern_atom("_NET_SUPPORTED")
        feature_atom = self.xdpy.intern_atom(feature)
        return (
            feature_atom
            in self.root.get_full_property(
                request, Xlib.X.AnyPropertyType
            ).value
        )

    def _assert_ewmh_support(self, feature: str, what_for: str) -> None:
        if not self._ewmh_is_supported(feature):
            raise XdoError(
                f"Your windowmanager claims not to support {feature}, "
                f"so the attempt to {what_for} was aborted."
            )

    def get_active_window(self) -> int:
        self._assert_ewmh_support(
            "_NET_ACTIVE_WINDOW", "query the active window"
        )
        return self._get_required_int_property("_NET_ACTIVE_WINDOW")

    def get_desktop_for_window(self, window_id: int) -> int:
        self._assert_ewmh_support(
            "_NET_WM_DESKTOP", "query a window's desktop location"
        )

        return self._get_required_int_property("_NET_WM_DESKTOP", window_id)

    def set_desktop_for_window(self, window_id: int, desktop: int) -> None:
        self._assert_ewmh_support(
            "_NET_WM_DESKTOP", "change a window's desktop location"
        )

        self._set_property(
            "_NET_WM_DESKTOP",
            [2, desktop],  # 2 == Message from a window pager
            window_id,
        )

    def get_current_desktop(self) -> int:
        self._assert_ewmh_support(
            "_NET_CURRENT_DESKTOP", "query for the current desktop"
        )
        return self._get_required_int_property("_NET_CURRENT_DESKTOP")

    def set_current_desktop(self, desktop: int) -> None:
        self._assert_ewmh_support("_NET_CURRENT_DESKTOP", "change desktops")
        self._set_property(
            "_NET_CURRENT_DESKTOP", [desktop, Xlib.X.CurrentTime]
        )

    def wait_for_window_active(self, window_id: int, active: bool) -> None:
        """If active is true, wait until activewin is our window
        otherwise, wait until activewin is not our window.
        """
        for _ in range(MAX_TRIES):
            active_window_id = self.get_active_window()
            if active:
                if active_window_id == window_id:
                    return
            elif active_window_id != window_id:
                return
            time.sleep(0.03)

    def activate_window(self, window_id: int) -> None:
        self._assert_ewmh_support("_NET_ACTIVE_WINDOW", "activate the window")

        # If this window is on another desktop, let's go to that desktop first
        if self._ewmh_is_supported(
            "_NET_WM_DESKTOP"
        ) and self._ewmh_is_supported("_NET_CURRENT_DESKTOP"):
            desktop = self.get_desktop_for_window(window_id)
            self.set_current_desktop(desktop)

        self._set_property(
            "_NET_ACTIVE_WINDOW",
            [2, Xlib.X.CurrentTime],  # 2 == Message from a window pager
            window_id,
        )

    def get_number_of_desktops(self) -> int:
        self._assert_ewmh_support(
            "_NET_NUMBER_OF_DESKTOPS", "query the number of desktops"
        )
        return self._get_required_int_property("_NET_NUMBER_OF_DESKTOPS")

    def set_number_of_desktops(self, num_desktops: int) -> None:
        self._assert_ewmh_support(
            "_NET_NUMBER_OF_DESKTOPS", "query the number of desktops"
        )
        self._set_property(
            "_NET_NUMBER_OF_DESKTOPS",
            [num_desktops],
        )

    def _get_property(
        self,
        atom_name: str,
        window_id: Optional[int] = None,
        allow_empty: bool = False,
    ) -> Any:
        request = self.xdpy.intern_atom(atom_name)
        if window_id:
            win = self.xdpy.create_resource_object("window", window_id)
        else:
            win = self.root
        data = win.get_full_property(request, Xlib.X.AnyPropertyType)
        if not data:
            raise XdoError(f"XGetWindowProperty[{atom_name}]")
        if not data.value:
            if not allow_empty:
                raise XdoError(f"XGetWindowProperty[{atom_name}]")
            return None

        return data.value

    def _get_required_int_property(
        self, atom_name: str, window_id: Optional[int] = None
    ) -> int:
        ret = self._get_property(atom_name, window_id, allow_empty=False)
        assert ret is not None
        return cast(int, ret[0])

    def _get_optional_int_property(
        self, atom_name: str, window_id: Optional[int] = None
    ) -> Optional[int]:
        ret = self._get_property(atom_name, window_id, allow_empty=False)
        if ret is None:
            return None
        return cast(Optional[int], ret[0])

    def _get_string_property(
        self,
        atom_name: str,
        window_id: Optional[int] = None,
        allow_empty: bool = False,
    ) -> Optional[str]:
        ret = self._get_property(atom_name, window_id, allow_empty)
        if ret is None:
            return ret
        return "".join(map(chr, ret))

    def _set_property(
        self,
        atom_name: str,
        data: Union[str, list[Any]],
        window_id: Optional[int] = None,
        target_window_id: Optional[int] = None,
        mask: Optional[int] = None,
    ) -> None:
        """Send a ClientMessage event to the target window."""
        if target_window_id:
            target = self.xdpy.create_resource_object(
                "window", target_window_id
            )
        else:
            target = self.root

        if window_id:
            win = self.xdpy.create_resource_object("window", window_id)
        else:
            win = self.root

        if isinstance(data, str):
            data_size = 8
        else:
            data = (data + [0] * (5 - len(data)))[:5]
            data_size = 32

        atom = self.xdpy.get_atom(atom_name)
        event = Xlib.protocol.event.ClientMessage(
            window=win, client_type=atom, data=(data_size, data)
        )

        if not mask:
            mask = (
                Xlib.X.SubstructureRedirectMask | Xlib.X.SubstructureNotifyMask
            )

        ret = target.send_event(event, event_mask=mask)
        if ret:
            raise XdoError(f"XSendEvent[{atom_name}]")

    def get_focused_window(self) -> int:
        return cast(int, self.xdpy.get_input_focus().focus.id)

    def get_focused_window_sane(self) -> int:
        window_ret = self.find_window_client(
            self.get_focused_window(), XdoSearchDirection.CHILDREN
        )
        if not window_ret:
            raise XdoError("Xdo.get_focused_window_sane")
        return window_ret

    def find_window_client(
        self, window_id: int, direction: XdoSearchDirection
    ) -> Optional[int]:
        window = self.xdpy.create_resource_object("window", window_id)

        while True:
            if not window:
                return None

            if self._get_optional_int_property("WM_STATE", window_id):
                return cast(int, window.id)

            # This window doesn't have WM_STATE property, keep searching.
            result = window.query_tree()

            if direction == XdoSearchDirection.PARENTS:
                window = result.parent

            elif direction == XdoSearchDirection.CHILDREN:
                for child_window in result.children:
                    window_ret = self.find_window_client(
                        child_window.id, direction
                    )
                    if window_ret is not None:
                        return window_ret
                return None

            else:
                assert False, "invalid search direction"

    def get_window_name(self, window_id: int) -> Optional[str]:
        ret = self._get_string_property(
            "_NET_WM_NAME", window_id, allow_empty=True
        )
        if ret is None:
            ret = self._get_string_property(
                "WM_NAME", window_id, allow_empty=True
            )
        return ret

    def get_window_pid(self, window_id: int) -> Optional[int]:
        return self._get_required_int_property("_NET_WM_PID", window_id)

    def get_window_size(self, window_id: int) -> tuple[int, int]:
        win = self.xdpy.create_resource_object("window", window_id)
        geometry = win.get_geometry()
        return geometry.width, geometry.height

    def get_window_location(
        self, window_id: int
    ) -> tuple[int, int, Optional[int]]:
        win = self.xdpy.create_resource_object("window", window_id)
        geometry = win.get_geometry()

        parent = win.query_tree().parent
        root = win.query_tree().root
        if parent == root:
            win_x = geometry.x
            win_y = geometry.y
        else:
            translated_coords = root.translate_coords(win, 0, 0)
            win_x = translated_coords.x
            win_y = translated_coords.y

        win_w = geometry.width
        win_h = geometry.height

        screen_id: Optional[int] = None
        for screen in self.query_screens():
            if (
                screen.x <= win_x < screen.x + screen.width
                and screen.y <= win_y < screen.y + screen.height
            ):
                screen_id = screen.num
                break
        else:
            for screen in self.query_screens():
                if (
                    screen.x <= win_x + win_w < screen.x + screen.width
                    and screen.y <= win_y + win_h < screen.y + screen.height
                ):
                    screen_id = screen.num
                    break
        return win_x, win_y, screen_id

    def move_window(
        self, window_id: int, target_x: int, target_y: int
    ) -> None:
        win = self.xdpy.create_resource_object("window", window_id)
        win.configure(x=target_x, y=target_y)

    def get_screen_size(self, screen_id: int) -> tuple[int, int]:
        try:
            screen = list(self.query_screens())[screen_id]
        except IndexError as ex:
            raise IndexError(f"Invalid screen {screen_id!r}") from ex
        else:
            return screen.width, screen.height

    def get_screen_location(self, screen_id: int) -> tuple[int, int]:
        try:
            screen = list(self.query_screens())[screen_id]
        except IndexError as ex:
            raise IndexError(f"Invalid screen {screen_id!r}") from ex
        else:
            return screen.x, screen.y

    def query_screens(self) -> Iterable[XdoScreenInfo]:
        return [
            XdoScreenInfo(
                num=i,
                x=screen.x,
                y=screen.y,
                width=screen.width,
                height=screen.height,
            )
            for i, screen in enumerate(
                self.xdpy.xinerama_query_screens().screens
            )
        ]
