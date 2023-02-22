"""Provides the base code and implementations of toggle widgets.

In particular it provides `Checkbox`, `RadioButton` and `RadioSet`.
"""

from __future__ import annotations

from typing import ClassVar

from rich.style import Style
from rich.text import Text, TextType

from ..app import RenderResult
from ..binding import Binding, BindingType
from ..message import Message
from ..reactive import reactive
from ._static import Static


class ToggleButton(Static, can_focus=True):
    """Base toggle button widget."""

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("enter,space", "toggle", "Toggle", show=False),
    ]
    """
    | Key(s) | Description |
    | :- | :- |
    | enter,space | Toggle the value. |
    """

    COMPONENT_CLASSES: ClassVar[set[str]] = {
        "toggle--button",
        "toggle--label",
    }
    """
    | Class | Description |
    | :- | :- |
    | `toggle--button` | Targets toggle button itself. |
    | `toggle--label` | Targets the text label of the toggle button. |
    """

    DEFAULT_CSS = """
    ToggleButton:hover {
        text-style: bold;
        background: $boost;
    }

    ToggleButton:focus > .toggle--label {
        text-style: underline;
    }

    /* Base button colours (including in dark mode). */

    ToggleButton > .toggle--button {
        color: $background;
        background: $foreground 15%;
    }

    ToggleButton:focus > .toggle--button {
        background: $foreground 25%;
    }

    ToggleButton.-on > .toggle--button {
        color: $success;
    }

    ToggleButton.-on:focus > .toggle--button {
        background: $foreground 25%;
    }

    /* Light mode overrides. */

    App.-light-mode ToggleButton > .toggle--button {
        color: $background;
        background: $foreground 10%;
    }

    App.-light-mode ToggleButton:focus > .toggle--button {
        background: $foreground 25%;
    }

    App.-light-mode ToggleButton.-on > .toggle--button {
        color: $primary;
    }
    """  # TODO: https://github.com/Textualize/textual/issues/1780

    BUTTON_LEFT: str = "▐"
    """The character for the left side of the toggle button."""

    BUTTON_INNER: str = "✖"
    """The character used to for the inside of the button."""

    BUTTON_RIGHT: str = "▌"
    """The character for the right side of the toggle button."""

    value: reactive[bool] = reactive(False)
    """The value of the button. `True` for on, `False` for off."""

    def __init__(
        self,
        label: TextType,
        value: bool = False,
        button_first: bool = True,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        """Initialise the toggle.

        Args:
            label: The label for the toggle.
            value: The initial value of the toggle. Defaults to `False`.
            button_first: Should the button come before the label, or after?
            name: The name of the toggle.
            id: The ID of the toggle in the DOM.
            classes: The CSS classes of the toggle.
            disabled: Whether the button is disabled or not.
        """
        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self._button_first = button_first
        self.value = value
        self.label: Text = Text.from_markup(label) if isinstance(label, str) else label
        """The label for the button."""

    @property
    def _button(self) -> Text:
        """The button, reflecting the current value."""

        # Grab the button style.
        button_style = self.get_component_rich_style("toggle--button")

        # If the button is off, we're going to do a bit of a switcharound to
        # make it look like it's a "cutout".
        if not self.value:
            button_style = Style.from_color(
                self.background_colors[1].rich_color, button_style.bgcolor
            )

        # Building the style for the side characters. Note that this is
        # sensitive to the type of character used, so pay attention to
        # BUTTON_LEFT and BUTTON_RIGHT.
        side_style = Style.from_color(
            button_style.bgcolor, self.background_colors[1].rich_color
        )

        return Text.assemble(
            Text(self.BUTTON_LEFT, style=side_style),
            Text(self.BUTTON_INNER, style=button_style),
            Text(self.BUTTON_RIGHT, style=side_style),
        )

    def render(self) -> RenderResult:
        """Render the content of the widget.

        Returns:
            The content to render for the widget.
        """
        button = self._button
        label = self.label.copy()
        label.stylize(self.get_component_rich_style("toggle--label", partial=True))
        spacer = Text(" " if self.label else "")
        return (
            Text.assemble(button, spacer, label)
            if self._button_first
            else Text.assemble(label, spacer, button)
        )

    def toggle(self) -> None:
        """Toggle the value of the widget."""
        self.value = not self.value

    def action_toggle(self) -> None:
        """Toggle the value of the widget."""
        self.toggle()

    def on_click(self) -> None:
        """Toggle the value of the widget."""
        self.toggle()

    class Changed(Message, bubble=True):
        """Posted when the value of the toggle button."""

        def __init__(self, sender: ToggleButton, value: bool) -> None:
            """Initialise the message.

            Args:
                sender: The toggle button sending the message.
                value: The value of the toggle button.
            """
            super().__init__(sender)
            self.input = sender
            """A reference to the toggle button that was changed."""
            self.value = value
            """The value of the toggle button after the change."""

    def watch_value(self) -> None:
        """React to the value being changed."""
        self.set_class(self.value, "-on")
        self.post_message_no_wait(self.Changed(self, self.value))
