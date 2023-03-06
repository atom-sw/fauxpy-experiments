from abc import abstractmethod
from typing import List, Tuple


class ScoredEntity:
    def __init__(self,
                 file_path: str,
                 score: float):
        self._file_path = file_path
        self._score = score

    def get_score(self):
        return self._score


class ScoredStatement(ScoredEntity):
    def __init__(self, file_path: str, score: float, line_number: int):
        super().__init__(file_path, score)
        self._line_number = line_number

    def _pretty_representation(self):
        return f"{self._file_path} L:{self._line_number} S:{self._score}"

    def __repr__(self):
        return self._pretty_representation()

    def __str__(self):
        return self._pretty_representation()


class ScoredFunction(ScoredEntity):
    def __init__(self, file_path: str, score: float, function_range: Tuple[int, int], function_name: str):
        super().__init__(file_path, score)
        self._function_range = function_range
        self._function_name = function_name

    def _pretty_representation(self):
        return f"{self._file_path} N:{self._function_name} R:{self._function_range} S:{self._score}"

    def __repr__(self):
        return self._pretty_representation()

    def __str__(self):
        return self._pretty_representation()


class RankedEntity:
    def __init__(self,
                 scored_entity: ScoredEntity,
                 entity_rank: int):
        self._scored_entity = scored_entity
        self._entity_rank = entity_rank

    def _pretty_representation(self):
        return f"{self._scored_entity} -- {self._entity_rank}"

    def __repr__(self):
        return self._pretty_representation()

    def __str__(self):
        return self._pretty_representation()


class Ranker:
    def __init__(self):
        pass

    @abstractmethod
    def rank(self, scored_entities: List[ScoredEntity]) -> Tuple[List[RankedEntity], int]:
        pass


class BestCaseRanker(Ranker):
    def __init__(self):
        super().__init__()

    def rank(self, scored_entities: List[ScoredEntity]) -> Tuple[List[RankedEntity], int]:
        """
        Takes a list of scored entities, and returns a list of
        ranked entities, containing the rank of each scored entity, along
        with a value to be used as the rank of any entity
        not existing within the scored entities.
        """
        if len(scored_entities) == 0:
            return [], 1

        ranked_entities = []
        previous_score = scored_entities[0].get_score()
        previous_rank = 1
        for item in scored_entities:
            current_score = item.get_score()
            if current_score == previous_score:
                current_rank = previous_rank
            else:
                assert current_score < previous_score
                current_rank = previous_rank + 1
                previous_rank = current_rank
                previous_score = current_score
            current_ranked_entity = RankedEntity(item, current_rank)
            ranked_entities.append(current_ranked_entity)

        rank_of_others = previous_rank + 1
        if previous_score == 0:
            rank_of_others = previous_rank

        return ranked_entities, rank_of_others


class WorstCaseRanker(Ranker):
    def __init__(self):
        super().__init__()

    def rank(self, scored_entities: List[ScoredEntity]) -> Tuple[List[RankedEntity], int]:
        pass


class AverageCaseRanker(Ranker):
    def __init__(self):
        super().__init__()

    def rank(self, scored_entities: List[ScoredEntity]) -> Tuple[List[RankedEntity], int]:
        pass
