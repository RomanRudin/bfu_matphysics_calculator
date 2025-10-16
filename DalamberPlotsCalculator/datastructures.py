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
    
    def integrate(self, previous_sum: float) -> Plot:
        result = []
        sums = [previous_sum]
        if self.x0 < 0:
            if self.x1 <= 0:
                result.append(Segment(self.x0, self.x1, lambda x: sums[0] - 1 * (self(x)) * (x - self.x0)))
                sums.append(sums[0] - 1 * (self(self.x1)) * (self.x1 - self.x0))
            else:
                result.append(Segment(self.x0, 0, lambda x: sums[0] - 1 * (self(x)) * (x - self.x0)))
                sums.append(sums[0] - 1 * (self(0)) * (0 - self.x0))
                result.append(Segment(0, self.x1, lambda x: sums[1] + 1 * (self(x)) * (x - 0)))
                sums.append(sums[1] + 1 * (self(self.x1)) * (self.x1 - 0))
        else:
            result.append(Segment(self.x0, self.x1, lambda x: sums[0] +  (self(x)) * (x - self.x0)))
            sums.append(sums[0] + 1 * (self(self.x1)) * (self.x1 - self.x0))
        return Plot(result), sums[-1]
    
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

    def integrate(self) -> Plot:
        result = []
        previous_sum = 0
        for segment in self.segments:
            integrated, previous_sum = segment.integrate(previous_sum)
            print(integrated, previous_sum)
            for segment in integrated.segments:
                result.append(segment)
        return Plot(result)
    
    def __call__(self, x: float) -> float:
        if not self.segments: return 0
        if x < self.start: return self(self.start) 
        if x > self.end: return self(self.end)
        i = 0
        try:
            while not self.segments[i].x0 <= x <= self.segments[i].x1: 
                i += 1
        except Exception as e:
            i = 0
            with open('debug_log.txt', 'w') as file:
                file.write(str(self) + 2 * '\n')
                file.write(str(x) + 2 * '\n')
                while not self.segments[i].x0 <= x <= self.segments[i].x1: 
                    file.write(f'{str(self.segments[i].x0)}, {str(self.segments[i].x1)}, {str(i)}\n')
                    i += 1
            raise e
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
        return self.segments[0].x0
    @property
    def end(self) -> float:
        return self.segments[-1].x1

    def extend(self, amount: float) -> Plot:
        num = amount
        # print(self, self.start, self.end, num)
        return Plot([Segment(self.start - num, self.start, lambda _: self(self.start))] + \
            self.segments + [Segment(self.end, self.end + num, lambda _: self(self.end))])
    