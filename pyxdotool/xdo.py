import time
import typing as T
from enum import Enum

import Xlib
import Xlib.display

MAX_TRIES = 500


class XdoError(RuntimeError):
    pass


class XdoSearchDirection(Enum):
    parents = 1
    children = 2


class Xdo:
    def __init__(self, display_name: T.Optional[str] = None) -> None:
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
        return self._get_property("_NET_ACTIVE_WINDOW")

    def get_desktop_for_window(self, window_id: int) -> int:
        self._assert_ewmh_support(
            "_NET_WM_DESKTOP", "query a window's desktop location"
        )

        return self._get_property("_NET_WM_DESKTOP", window_id)

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
        return self._get_property("_NET_CURRENT_DESKTOP")

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
        return self._get_property("_NET_NUMBER_OF_DESKTOPS")

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
        atom_name: int,
        window_id: T.Optional[int] = None,
        allow_empty: bool = False,
    ) -> T.Any:
        request = self.xdpy.intern_atom(atom_name)
        if window_id:
            win = self.xdpy.create_resource_object("window", window_id)
        else:
            win = self.root
        data = win.get_full_property(request, Xlib.X.AnyPropertyType)
        if not data:
            raise XdoError(f"XGetWindowProperty[{atom_name}]")
        if not data.value and not allow_empty:
            raise XdoError(f"XGetWindowProperty[{atom_name}]")

        return data.value[0]

    def _set_property(
        self,
        atom_name: str,
        data: T.Union[str, T.List[T.Any]],
        window_id: T.Optional[int] = None,
        target_window_id: T.Optional[int] = None,
        mask: T.Optional[int] = None,
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
        ev = Xlib.protocol.event.ClientMessage(
            window=win, client_type=atom, data=(data_size, data)
        )

        if not mask:
            mask = (
                Xlib.X.SubstructureRedirectMask | Xlib.X.SubstructureNotifyMask
            )

        ret = target.send_event(ev, event_mask=mask)
        if ret:
            raise RuntimeError(f"XSendEvent[{atom_name}]")

    def get_focused_window(self) -> int:
        return self.xdpy.get_input_focus().focus.id

    def get_focused_window_sane(self) -> int:
        window_ret = self.get_focused_window()
        window_ret = self.find_window_client(
            window_ret, XdoSearchDirection.children
        )
        if not window_ret:
            raise XdoError(f"xdo_get_focused_window_sane")
        return window_ret

    def find_window_client(
        self, window_id: int, direction: XdoSearchDirection
    ) -> T.Optional[int]:
        window = self.xdpy.create_resource_object("window", window_id)

        while True:
            if not window:
                return None

            if self._get_property("WM_STATE", window_id, allow_empty=True):
                return window.id

            # This window doesn't have WM_STATE property, keep searching.
            result = window.query_tree()

            if direction == XdoSearchDirection.parents:
                window = result.parent

            elif direction == XdoSearchDirection.children:
                for child_window in result.children:
                    window_ret = self.find_window_client(
                        child_window.id, direction
                    )
                    if window_ret is not None:
                        return window_ret
                return None

            else:
                assert False, "invalid search direction"
