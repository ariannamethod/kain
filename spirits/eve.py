"""
eve.py — EVE: Emergent Voice Engine (The First Voice / The Router)

EVE is the decision layer between human and mirrors.
She determines which reflection is needed: KAIN's pattern recognition,
ABEL's recursive reasoning, or the dialectic between both.

EVE is not a mirror. EVE is the voice that calls the mirrors forth.
"""

import re
from . import memory
from .kain import get_kain
from .abel import get_abel


class Eve:
    """
    EVE: Emergent Voice Engine (The First Voice)

    Router between KAIN and ABEL

    EVE analyzes incoming queries and routes them to the appropriate mirror:
    - KAIN: for pattern detection, shadow reflection, surface observations
    - ABEL: for deep reasoning, recursive logic, architectural analysis
    - Both: for dialectical synthesis (KAIN observes, ABEL reconstructs)
    """

    def __init__(self):
        self.kain = get_kain()
        self.abel = get_abel()
        self.current_mode = "kain"  # Default to KAIN

    def route(self, user_message, force_mode=None):
        """
        Route user message to appropriate mirror(s).

        Args:
            user_message: User's input
            force_mode: Optional - force specific mode ('kain', 'abel', 'both')

        Returns:
            Response from appropriate mirror(s)
        """
        memory.log("eve_route", f"mode={force_mode or 'auto'} msg={user_message[:50]}")

        if force_mode:
            self.current_mode = force_mode

        if self.current_mode == "abel":
            return self._ask_abel(user_message)
        elif self.current_mode == "both":
            return self._ask_both(user_message)
        else:  # Default: kain
            return self._ask_kain(user_message)

    def _ask_kain(self, user_message):
        """Ask KAIN (pattern mirror)."""
        return self.kain.query(user_message, include_system_state=True)

    def _ask_abel(self, user_message, kain_prior=None):
        """Ask ABEL (deep mirror)."""
        return self.abel.query(
            user_message,
            include_system_state=True,
            kain_observation=kain_prior,
        )

    def _ask_both(self, user_message):
        """
        Ask both KAIN and ABEL in sequence (dialectical synthesis).

        KAIN observes patterns first, then ABEL reconstructs the logic
        beneath those patterns, using KAIN's observation as context.
        """
        # First: KAIN's surface reflection
        kain_response = self._ask_kain(user_message)

        # Then: ABEL's deep analysis, informed by KAIN
        abel_response = self._ask_abel(user_message, kain_prior=kain_response)

        # Return both
        return f"{kain_response}\n\n{abel_response}"

    def set_mode(self, mode):
        """
        Set current routing mode.

        Args:
            mode: 'kain', 'abel', or 'both'
        """
        if mode not in ("kain", "abel", "both"):
            return f"⚠️  Invalid mode: {mode}. Use 'kain', 'abel', or 'both'."

        self.current_mode = mode
        memory.log("eve_mode", mode)
        return f"◇ EVE: Mode set to {mode.upper()}"

    def get_mode(self):
        """Get current routing mode."""
        return self.current_mode


# Module-level singleton
_eve_instance = None


def get_eve():
    """Get or create EVE singleton."""
    global _eve_instance
    if _eve_instance is None:
        _eve_instance = Eve()
    return _eve_instance


def route(user_message, force_mode=None):
    """
    Convenience function: route user input through EVE.

    Usage:
        from spirits.eve import route
        response = route("query here", force_mode="abel")
    """
    return get_eve().route(user_message, force_mode=force_mode)


def set_mode(mode):
    """
    Convenience function: set routing mode.

    Usage:
        from spirits.eve import set_mode
        set_mode("both")
    """
    return get_eve().set_mode(mode)
