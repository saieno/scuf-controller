#!/usr/bin/python3
"""Validate the shipped profiles without needing hardware or root.

Run directly, or via `make check`. Contributors adding a controller should get
a clear failure here rather than a silent mis-mapping at runtime.
"""

import importlib.util
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_daemon():
    spec = importlib.util.spec_from_loader("scuf_controller", None)
    module = importlib.util.module_from_spec(spec)
    source = open(os.path.join(ROOT, "scuf-controller")).read()
    source = source.replace('if __name__ == "__main__":\n    sys.exit(main())', "")
    exec(source, module.__dict__)
    return module


def main():
    sc = load_daemon()
    profile_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "profiles")
    profiles = sc.load_profiles([profile_dir])

    if not profiles:
        print(f"FAIL: no profiles loaded from {profile_dir}", file=sys.stderr)
        return 1

    errors = []
    warnings = []

    for name, profile in sorted(profiles.items()):
        if not profile.axes:
            errors.append(f"{name}: no [axes] mappings")
        if not profile.buttons:
            errors.append(f"{name}: no [buttons] mappings")

        # Nothing distinguishes the profile from any other pad.
        m = profile.match
        if not any((m.vendor, m.product, m.name_re, m.buttons,
                    m.not_buttons, m.axes)):
            errors.append(f"{name}: [match] is empty, so it matches every pad")

        # Two source controls quietly fighting over one output is the single
        # easiest mistake to make when hand-writing a profile.
        seen = {}
        for src, dest in profile.buttons.items():
            seen.setdefault(dest, []).append(src)
        for dest, srcs in sorted(seen.items()):
            if len(srcs) > 1:
                warnings.append(
                    f"{name}: {', '.join(sc.button_name(s) for s in srcs)} "
                    f"all map to {sc.button_name(dest)}")

        axis_seen = {}
        for src, (dest, _kind) in profile.axes.items():
            axis_seen.setdefault(dest, []).append(src)
        for dest, srcs in sorted(axis_seen.items()):
            if len(srcs) > 1:
                warnings.append(
                    f"{name}: {', '.join(sc.axis_name(s) for s in srcs)} "
                    f"all map to {sc.axis_name(dest)}")

        # A digital trigger only makes sense on an axis declared as a trigger.
        for src, dest in profile.digital_triggers.items():
            kinds = {kind for (d, kind) in profile.axes.values() if d == dest}
            if kinds and sc.TRIGGER not in kinds:
                errors.append(
                    f"{name}: {sc.button_name(src)} drives {sc.axis_name(dest)}, "
                    f"which [axes] declares as {'/'.join(sorted(kinds))}")

        undriven = [c for c in sc.XBOX360_BUTTONS
                    if c not in set(profile.buttons.values())]
        driven_axes = {d for d, _ in profile.axes.values()}
        driven_axes |= set(profile.digital_triggers.values())
        undriven += [c for c, _ in sc.XBOX360_AXES if c not in driven_axes]

        print(f"  {name}: {len(profile.axes)} axes, {len(profile.buttons)} buttons, "
              f"{len(profile.digital_triggers)} digital triggers")
        if undriven:
            names = ", ".join(sc.button_name(c) if c in sc.XBOX360_BUTTONS
                              else sc.axis_name(c) for c in undriven)
            print(f"      xpad outputs nothing drives: {names}")

    for w in warnings:
        print(f"  warning: {w}", file=sys.stderr)
    for err in errors:
        print(f"  FAIL: {err}", file=sys.stderr)

    if errors:
        return 1
    print(f"{len(profiles)} profile(s) valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
