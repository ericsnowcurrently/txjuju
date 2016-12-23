# Copyright 2016 Canonical Limited.  All rights reserved.

from ._utils import namedtuple


WILDCARD = "x"

RELEASE_ALPHA = "alpha"
RELEASE_BETA = "beta"
RELEASE_CANDIDATE = "rc"
RELEASE_FINAL = "final"


def _releaselevel_matches(level, candidates):
    if not isinstance(level, str):
        return False
    for kind in candidates:
        if level.startswith(kind):
            # At this point no other kind will match, so we can return early.
            try:
                num = int(level[len(kind):])
            except ValueError:
                return False
            if num < 1:  # Releases are always 1-indexed.
                return False
            return True
    else:
        return False


def _is_dev_releaselevel(level):
    return _releaselevel_matches(level, (
            RELEASE_ALPHA,
            RELEASE_BETA,
            RELEASE_CANDIDATE,
            ))


def _is_valid_releaselevel(level):
    if not level or level == RELEASE_FINAL:
        return True
    return _is_dev_releaselevel(level)


def _is_valid_series(series):
    # TODO: Implement the check later, if necessary.
    return True


def _is_valid_arch(arch):
    # TODO: Implement the check later, if necessary.
    return True


def _parse_number(raw):
    if raw is None or raw == "":
        return None
    if raw in ("x", "X", "*"):
        return WILDCARD
    try:
        return int(raw)
    except TypeError, ValueError:
        return raw


class VersionNumber(namedtuple("VersionNumber", "major minor micro")):
    """A Juju version number or wildcard (e.g. 2.0, 1.25.6, 2.x)."""

    @classmethod
    def parse(cls, raw):
        """Return a VersionNumber corresponding to the given string.

        This round-trips with str(version).
        """
        major, _, raw = raw.partition(".")
        minor, sep, micro = raw.partition(".")
        if sep and not micro:
            raise ValueError("missing micro")
        return cls(major, minor, micro)

    def __new__(cls, major, minor, micro=None):
        major = _parse_number(major)
        minor = _parse_number(minor)
        micro = _parse_number(micro)
        return super(VersionNumber, cls).__new__(cls, major, minor, micro)

    def __init__(self, *args, **kwargs):
        super(VersionNumber, self).__init__(*args, **kwargs)
        self._validate()

    def _validate(self):
        invalid = "{} must be a non-negative integer, got {!r}"

        if self.major == WILDCARD:
            raise ValueError("wildcard not supported for the major version")
        elif not isinstance(self.major, int) or self.major < 0:
            raise ValueError(invalid.format("major", self.major))

        if self.minor == WILDCARD:
            if self.micro is not None:
                msg = "got unexpected micro ({}) with wildcard minor"
                raise ValueError(msg.format(self.micro))
        elif not isinstance(self.minor, int) or self.minor < 0:
            raise ValueError(invalid.format("minor", self.minor))

        if self.micro is not None and self.micro != WILDCARD:
            if not isinstance(self.micro, int) or self.micro < 0:
                raise ValueError(invalid.format("micro", self.micro))

        if not self.major and not self.minor and not self.micro:
            raise ValueError(
                "at least one of major, minor, and micro must be set")

    def __str__(self):
        if self.micro is None:
            return "{}.{}".format(self.major, self.minor)
        return "{}.{}.{}".format(self.major, self.minor, self.micro)

    @property
    def iswildcard(self):
        """Whether or not it's a wildcard version."""
        if self.minor == WILDCARD:
            return True
        if self.micro is None or self.micro == WILDCARD:
            return True
        return False

    def match(self, version):
        """Return True if the provided version matches and False otherwise."""
        if not isinstance(version, VersionNumber):
            version = type(self).parse(version)
        expected = self._apply(version)
        return version == expected

    def _apply(self, version):
        applied = self
        if applied.minor == WILDCARD:
            applied = applied._replace(minor=version.minor)
        if applied.micro is None or applied.micro == WILDCARD:
            applied = applied._replace(micro=version.micro)
        return applied


class Version(namedtuple("Version", "number releaselevel series arch")):
    """A Juju version."""

    @classmethod
    def parse(cls, raw):
        """Return a Version corresponding to the given string.

        This round-trips with str(version), except in the case of
        verbose version strings like "2.1.0-beta2" and "2.0.1-final".
        """
        num, sep, raw = raw.partition("-")
        num = VersionNumber.parse(num)
        if not sep:
            return cls(num)

        level, sep, raw = raw.partition("-")
        series = arch = None
        if sep:
            series, sep, arch = raw.partition("-")
            if not sep:
                arch = series
                series = level
                level = RELEASE_FINAL
        if num.micro is None and _is_dev_releaselevel(level):
            num = num._replace(micro=0)
        return cls(num, level, series, arch)

    def __new__(cls, number, releaselevel=None, series=None, arch=None):
        if number and not isinstance(number, VersionNumber):
            number = VersionNumber.parse(number)
        releaselevel = releaselevel.lower() if releaselevel else RELEASE_FINAL
        series = str(series).lower() if series else None
        arch = str(arch).lower() if arch else None
        return super(Version, cls).__new__(
            cls, number, releaselevel, series, arch)

    def __init__(self, *args, **kwargs):
        super(Version, self).__init__(*args, **kwargs)
        self._validate()

    def _validate(self):
        if not self.number:
            raise ValueError("missing number")
        if self.number.iswildcard:
            raise ValueError(
                "wildcard versions not supported ({})".format(self.number))

        if not self.releaselevel:
            raise ValueError("missing releaselevel")
        if not _is_valid_releaselevel(self.releaselevel):
            raise ValueError(
                "invalid releaselevel {!r}".format(self.releaselevel))

        if self.series and not _is_valid_series(self.series):
            raise ValueError("invalid series {!r}".format(self.series))

        if self.arch and not _is_valid_arch(self.arch):
            raise ValueError("invalid arch {!r}".format(self.arch))

        if self.series and not self.arch:
            raise ValueError("missing arch (have series)")
        if self.arch and not self.series:
            raise ValueError("missing series (have arch)")

    def __str__(self):
        ver = str(self.number)
        if self.releaselevel != RELEASE_FINAL:
            if self.number.micro == 0:
                ver = ver.rpartition(".")[0]
            ver += "-" + self.releaselevel
        if self.series:
            ver += "-" + self.series
        if self.arch:
            ver += "-" + self.arch
        return ver
