import time
import typing as T

import Xlib
import Xlib.display

MAX_TRIES = 500


class XdoError(RuntimeError):
    pass


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

        request = self.xdpy.intern_atom("_NET_ACTIVE_WINDOW")
        data = self.root.get_full_property(
            request, Xlib.X.AnyPropertyType
        ).value
        if not data:
            raise XdoError("XGetWindowProperty[_NET_ACTIVE_WINDOW]")

        return data[0]

    def get_desktop_for_window(self, window_id: int) -> int:
        self._assert_ewmh_support(
            "_NET_WM_DESKTOP", "query a window's desktop location"
        )

        request = self.xdpy.intern_atom("_NET_WM_DESKTOP")
        win = self.xdpy.create_resource_object("window", window_id)
        data = win.get_full_property(request, Xlib.X.AnyPropertyType).value
        if not data:
            raise RuntimeError("XGetWindowProperty[_NET_WM_DESKTOP]")

        return data[0]

    def set_desktop_for_window(self, window_id: int, desktop: int) -> None:
        self._assert_ewmh_support(
            "_NET_WM_DESKTOP", "change a window's desktop location"
        )

        self._set_property(
            "_NET_WM_DESKTOP",
            [2, desktop],  # 2 == Message from a window pager
            window_id,
        )

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
