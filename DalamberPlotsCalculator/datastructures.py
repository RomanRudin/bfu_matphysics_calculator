from __future__ import annotations
from dataclasses import dataclass
from typing import Callable

@dataclass
class Range:
    x0: float
    x1: float
    y0: float
    y1: float

    def x_length(self) -> float: return self.x1 - self.x0
    def x_range(self) -> list[float, float]: return [self.x0, self.x1]
    def y_range(self) -> list[float, float]: return [self.y0, self.y1]



    
@dataclass
class Segment:
    x0: float
    x1: float
    function: Callable
    
    def __add__(self, other: float | Segment) -> Segment:
        if type(other) == Segment: 
            assert self.x0 == other.x0 and self.x1 == other.x1
            return Segment(self.x0, other.x1, lambda x: self(x) + other(x))
        return Segment(self.x0, self.x1, lambda x: self(x) + other)
    def __sub__(self, other: float | Segment) -> Segment:
        if type(other) == Segment: 
            assert self.x0 == other.x0 and self.x1 == other.x1
            return Segment(self.x0, self.x1, lambda x: self(x) - other(x))
        return Segment(self.x0, self.x1, lambda x: self(x) - other)
    def __mul__(self, other: float | Segment) -> Segment:
        if type(other) == Segment: 
            assert self.x0 == other.x0 and self.x1 == other.x1
            return Segment(self.x0, other.x1, lambda x: self(x) * other(x))
        return Segment(self.x0, self.x1, lambda x: self(x) * other)
    def __div__(self, other: float | Segment) -> Segment:
        if type(other) == Segment: 
            assert self.x0 == other.x0 and self.x1 == other.x1
            return Segment(self.x0, self.x1, lambda x: self(x) / other(x))
        return Segment(self.x0, self.x1, lambda x: self(x) / other)
    def __radd__(self, other: float | Segment) -> Segment:
        if type(other) == Segment: 
            return other + self
        return Segment(self.x0, self.x1, lambda x: self(x) + other)
    def __rsub__(self, other: float | Segment) -> Segment:
        if type(other) == Segment: 
            return other - self
        return Segment(self.x0, self.x1, lambda x: other - self(x))
    def __rmul__(self, other: float | Segment) -> Segment:
        if type(other) == Segment: 
            return other * self
        return Segment(self.x0, self.x1, lambda x: self(x) * other)
    def __rdiv__(self, other: float | Segment) -> Segment:
        if type(other) == Segment: 
            return other / self
        return Segment(self.x0, self.x1, lambda x: other / self(x))
    
    def integrate(self, previous_sum: float) -> list[Plot, float]:
        if self.x1 < 0:
            previous_sum -= (self(self.x1)) * (self.x1 - self.x0)
            return Segment(self.x0, self.x1, lambda x: previous_sum + (self(x)) * (x - self.x0)), previous_sum
        return Segment(self.x0, self.x1, lambda x: previous_sum + (self(x)) * (x - self.x0)), previous_sum + (self(self.x1)) * (self.x1 - self.x0)

    def __call__(self, x: float) -> float:
        return self.function(x)
    def __str__(self) -> str:
        return f"Segment(start = {self.x0}, end = {self.x1}, function({self.x0}) = {self(self.x0)}, function({self.x1}) = {self(self.x1)})"''
    



class Plot:
    def __init__(self, segments: list[Segment]) -> None:
        self.segments = segments

    def __add__(self, other: float | Plot) -> Plot:
        if type(other) == Plot:
            if not self.segments: return other
            if not other.segments: return self
            result = []
            all_segments = self._split(other)
            for i in range(len(all_segments) - 1):
                current = Segment(all_segments[i], all_segments[i + 1], lambda x: 0)
                if all_segments[i] >= self.start and all_segments[i + 1] <= self.end:
                    current += Segment(all_segments[i], all_segments[i + 1], lambda x: self(x))
                if all_segments[i] >= other.start and all_segments[i + 1] <= other.end:
                    current += Segment(all_segments[i], all_segments[i + 1], lambda x: other(x))
                result.append(current)
            return Plot(result)
        return Plot([segment + other for segment in self.segments])
    def __sub__(self, other: float | Plot) -> Plot:
        if type(other) == Plot: 
            return self + other * (-1)
        return Plot([segment - other for segment in self.segments])
    def __mul__(self, other: float | Plot) -> Plot:
        if type(other) == Plot: 
            result = []
            all_segments = self._split(other)
            for i in  range(len(all_segments) - 1):
                current = Segment(all_segments[i], all_segments[i + 1], lambda x: 1)
                if all_segments[i] >= self.start and all_segments[i + 1] <= self.end:
                    current *= Segment(all_segments[i], all_segments[i + 1], lambda x: self(x))
                if all_segments[i] >= other.start and all_segments[i + 1] <= other.end:
                    current *= Segment(all_segments[i], all_segments[i + 1], lambda x: other(x))
                result.append(current)
            return Plot(result)
        return Plot([segment * other for segment in self.segments])
    def __div__(self, other: float | Plot) -> Plot:
        if type(other) == Plot: 
            result = []
            all_segments = self._split(other)
            for i in  range(len(all_segments) - 1):
                current = Segment(all_segments[i], all_segments[i + 1], lambda x: 1)
                if all_segments[i] >= self.start and all_segments[i + 1] <= self.end:
                    current *= Segment(all_segments[i], all_segments[i + 1], lambda x: self(x))
                if all_segments[i] >= other.start and all_segments[i + 1] <= other.end:
                    current /= Segment(all_segments[i], all_segments[i + 1], lambda x: other(x))
                result.append(current)
            return Plot(result)
        return Plot([segment / other for segment in self.segments])
    def __radd__(self, other: float | Plot) -> Plot:
        if type(other) == Plot: \
            return other + self
        return Plot([segment + other for segment in self.segments])
    def __rsub__(self, other: float | Plot) -> Plot:
        if type(other) == Plot: 
            return other - self
        return Plot([segment - other for segment in self.segments])
    def __rmul__(self, other: float | Plot) -> Plot:
        if type(other) == Plot: 
            return other * self
        return Plot([segment * other for segment in self.segments])
    def __rdiv__(self, other: float | Plot) -> Plot:
        if type(other) == Plot: 
            return other / self
        return Plot([segment / other for segment in self.segments])
    
    def _split(self, other: Plot) -> list[float]:
        all_segments = []
        for segment in self.segments:
            if segment.x0 not in all_segments:
                all_segments.append(segment.x0)
            if segment.x0 not in all_segments:
                all_segments.append(segment.x1)
        for segment in other.segments:
            if segment.x0 not in all_segments:
                all_segments.append(segment.x0)
            if segment.x1 not in all_segments:
                all_segments.append(segment.x1)
        return sorted(all_segments)
    
    def _split_zero(self) -> float:
        if self.end <= 0:
            return len(self.segments)
        if self.start >= 0:
            return 0
        for zero_index, segment in enumerate(self.segments):
            if segment.x0 == 0:
                return zero_index
            if segment.x0 < 0 < segment.x1:
                deleted_segment = self.segments.pop(zero_index)
                self.segments.insert(zero_index, Segment(0, deleted_segment.x1, lambda x: deleted_segment(x)))
                self.segments.insert(zero_index, Segment(deleted_segment.x0, 0, lambda x: deleted_segment(x)))
                return zero_index

    def integrate(self) -> Plot:
        if self.segments == []: return self
        result = []
        previous_sum = 0
        zero_index = self._split_zero()
        for i in range(zero_index, len(self.segments)):
            integrated, previous_sum = self.segments[i].integrate(previous_sum)
            result.append(integrated)
        previous_sum = 0
        for i in range(zero_index - 1, -1, -1):
            integrated, previous_sum = self.segments[i].integrate(previous_sum)
            result.insert(0, integrated)
        return Plot(result)
    
    def __call__(self, x: float) -> float:
        if not self.segments: return 0
        if x < self.start: return self(self.start) 
        if x > self.end: return self(self.end)
        while not self.segments[i].x0 <= x <= self.segments[i].x1: 
            i += 1
        return self.segments[i](x)

    def shift(self, shift_amount: float) -> Plot:
        new_segments = []
        for segment in self.segments:
            new_segment = Segment(
                segment.x0 + shift_amount,
                segment.x1 + shift_amount,
                lambda x, seg=segment, shift=shift_amount: seg(x - shift)
            )
            new_segments.append(new_segment)
        return Plot(new_segments)
    def __str__(self) -> str:
        return f"Plot(length = {len(self.segments)},\n{'\n'.join(str(segment) for segment in self.segments)}\n)"
    def __len__(self) -> Plot:
        return self.end - self.start
    
    @property
    def start(self) -> float:
        if not self.segments: return 0
        return self.segments[0].x0
    @property
    def end(self) -> float:
        return self.segments[-1].x1

    def extend(self, amount: float) -> Plot:
        num = amount
        return Plot([Segment(self.start - num, self.start, lambda _: self(self.start))] + \
            self.segments + [Segment(self.end, self.end + num, lambda _: self(self.end))])
    