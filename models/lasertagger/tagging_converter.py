# coding=utf-8
# Copyright 2019 The Google Research Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Conversion from training target text into target tags.

The conversion algorithm from (source, target) pairs to (source, target_tags)
pairs is described in Algorithm 1 of the LaserTagger paper
(https://arxiv.org/abs/1909.01187).
"""

from __future__ import absolute_import
from __future__ import division

from __future__ import print_function

import tagging
import utils


class TaggingConverter(object):
    """Converter from training target texts into tagging format."""
    def __init__(self,
                 phrase_vocabulary,
                 do_swap=True,
                 arbitrary_reordering=True):
        """Initializes an instance of TaggingConverter.

    Args:
      phrase_vocabulary: Iterable of phrase vocabulary items (strings).
      do_swap: Whether to enable the SWAP tag.
      arbitrary_reordering: Whether to use arbitrary reordering
    """
        self._phrase_vocabulary = set(phrase.lower()
                                      for phrase in phrase_vocabulary)
        self._do_swap = do_swap
        # Maximum number of tokens in an added phrase (inferred from the
        # vocabulary).
        self._max_added_phrase_length = 0
        # Set of tokens that are part of a phrase in self.phrase_vocabulary.
        self._token_vocabulary = set()
        for phrase in self._phrase_vocabulary:
            tokens = utils.get_token_list(phrase)
            self._token_vocabulary |= set(tokens)
            if len(tokens) > self._max_added_phrase_length:
                self._max_added_phrase_length = len(tokens)

        self._arbitrary_reordering = arbitrary_reordering

        self._compute_tags_fixed_order = self._compute_tags_fixed_order_without_reordering
        if self._arbitrary_reordering:
            self._compute_tags_fixed_order = self._compute_tags_fixed_order_with_reordering

    def compute_tags(self, task, target):
        """Computes tags needed for converting the source into the target.

    Args:
      task: tagging.EditingTask that specifies the input.
      target: Target text.

    Returns:
      List of tagging.Tag objects. If the source couldn't be converted into the
      target via tagging, returns an empty list.
    """
        target_tokens = utils.get_token_list(target.lower())
        tags = self._compute_tags_fixed_order(task.source_tokens,
                                              target_tokens)
        # If conversion fails, try to obtain the target after swapping the source
        # order.
        if not self._arbitrary_reordering and not tags and len(
                task.sources) == 2 and self._do_swap:
            swapped_task = tagging.EditingTask(task.sources[::-1])
            tags = self._compute_tags_fixed_order(swapped_task.source_tokens,
                                                  target_tokens)
            if tags:
                tags = (tags[swapped_task.first_tokens[1]:] +
                        tags[:swapped_task.first_tokens[1]])
                # We assume that the last token (typically a period) is never deleted,
                # so we can overwrite the tag_type with SWAP (which keeps the token,
                # moving it and the sentence it's part of to the end).
                tags[task.first_tokens[1] - 1].tag_type = tagging.TagType.SWAP
        return tags

    def _compute_tags_fixed_order_without_reordering(self, source_tokens,
                                                     target_tokens):
        """Computes tags when the order of sources is fixed.

    Args:
      source_tokens: List of source tokens.
      target_tokens: List of tokens to be obtained via edit operations.

    Returns:
      List of tagging.Tag objects. If the source couldn't be converted into the
      target via tagging, returns an empty list.
    """
        tags = [tagging.Tag('DELETE') for _ in source_tokens]
        # Indices of the tokens currently being processed.
        source_token_idx = 0
        target_token_idx = 0
        while target_token_idx < len(target_tokens):
            #tags[source_token_idx], target_token_idx = self._compute_single_tag_mod(
            #    source_tokens[source_token_idx], target_token_idx, target_tokens, source_tokens)
            tags[
                source_token_idx], target_token_idx = self._compute_single_tag_without_reordering(
                    source_tokens[source_token_idx], target_token_idx,
                    target_tokens)
            # If we're adding a phrase and the previous source token(s) were deleted,
            # we could add the phrase before a previously deleted token and still get
            # the same realized output. For example:
            #    [DELETE, DELETE, KEEP|"what is"]
            # and
            #    [DELETE|"what is", DELETE, KEEP]
            # Would yield the same realized output. Experimentally, we noticed that
            # the model works better / the learning task becomes easier when phrases
            # are always added before the first deleted token. Also note that in the
            # current implementation, this way of moving the added phrase backward is
            # the only way a DELETE tag can have an added phrase, so sequences like
            # [DELETE|"What", DELETE|"is"] will never be created.
            if tags[source_token_idx].added_phrase and not tags[
                    source_token_idx].added_phrase.isnumeric():
                first_deletion_idx = self._find_first_deletion_idx(
                    source_token_idx, tags)
                if first_deletion_idx != source_token_idx:
                    tags[first_deletion_idx].added_phrase = (
                        tags[source_token_idx].added_phrase)
                    tags[source_token_idx].added_phrase = ''
            source_token_idx += 1
            if source_token_idx >= len(tags):
                break

        # If all target tokens have been consumed, we have found a conversion and
        # can return the tags. Note that if there are remaining source tokens, they
        # are already marked deleted when initializing the tag list.
        print([
            print("token: {0} - {1} ".format(source_tokens[i], str(label)))
            for i, label in enumerate(tags)
        ])

        if target_token_idx >= len(target_tokens):
            return tags

        return []

    def _compute_single_tag_without_reordering(self, source_token,
                                               target_token_idx,
                                               target_tokens):
        """Computes a single tag.

    The tag may match multiple target tokens (via tag.added_phrase) so we return
    the next unmatched target token.

    Args:
      source_token: The token to be tagged.
      target_token_idx: Index of the current target tag.
      target_tokens: List of all target tokens.

    Returns:
      A tuple with (1) the computed tag and (2) the next target_token_idx.
    """
        source_token = source_token.lower()
        target_token = target_tokens[target_token_idx].lower()
        if source_token == target_token:
            return tagging.Tag('KEEP'), target_token_idx + 1

        added_phrase = ''
        for num_added_tokens in range(1, self._max_added_phrase_length + 1):
            if target_token not in self._token_vocabulary:
                break
            added_phrase += (' ' if added_phrase else '') + target_token
            next_target_token_idx = target_token_idx + num_added_tokens
            if next_target_token_idx >= len(target_tokens):
                break
            target_token = target_tokens[next_target_token_idx].lower()
            if (source_token == target_token
                    and added_phrase in self._phrase_vocabulary):
                return tagging.Tag('KEEP|' +
                                   added_phrase), next_target_token_idx + 1
        return tagging.Tag('DELETE'), target_token_idx

    def _compute_tags_fixed_order_with_reordering(self, source_tokens,
                                                  target_tokens):
        """
            args:
                source_tokens - list of source tokens
                target_tokens - list of target tokens

            Computes tags for a given list of source tokens 
            and target tokens when arbitrary reordering is allowed.

            Source tokens list and the final tags returned 
            may no longer have the same number of elements
            since there is no longer a KEEP+ or DELETE+ 
            tag, and all additions are done by a separate 
            KEEP|<phrase> tag that is not associated with 
            any of the source tokens
        """
        # tags
        tags = []
        # extra addition from phrase vocab tags
        to_add_list = []

        source_token_idx, target_token_idx = 0, 0

        source_tokens = [src_token.lower() for src_token in source_tokens]

        while target_tokens.count("<NULL>") != len(
                target_tokens) and source_token_idx <= len(source_tokens):
            res = self._compute_single_tag_with_reordering(
                source_token_idx, target_token_idx, target_tokens,
                source_tokens)

            # generation is infeasible
            if res == 0:
                return []


            else:
                # if the tag is associated with a source token 
                # and not a position
                if res[3] == -1:
                    tags.append(res[0])
                else:
                    # associated with a position
                    to_add_list.append([res[0], res[3]])

                target_token_idx = res[1]
                source_token_idx = res[2]

        if target_tokens.count("<NULL>") != len(target_tokens):
            return []

        to_add_list = sorted(to_add_list, key=lambda x: x[1])
        
        # add the positional addition tags to the final tags list
        for tag, position in to_add_list:
            tags.insert(position, tag)

        return tags

    def _compute_single_tag_with_reordering(self, source_token_idx,
                                            target_token_idx, target_tokens,
                                            source_tokens):
        """Computes a single tag.

    args:
        source_token_idx: the current index of the source token
                            in the source tokens list
        target_token_idx: the current index of the target token
                            in the target token list
        target tokens: list of target tokens
        source_tokens: list of source_tokens

    returns: 
     Tag : the tag computed
     target token idx : updates and returns target token index
     source token idx : updates and returns source token index
     position to add at : a positive integer only in the case of
                    addition of phrases, -1 otherwise.
            This is necessary to ensure the correct position of 
            this tag in the final tags list

    The predicted tags can be:
    - KEEP|<position> 
    where position is the position at which the source token
    occurs in the target string.
    - KEEP|<phrase_to_add> 
    phrase_to_add is the phrase that is being added from the 
    edit vocabulary
    - DELETE
    source token does not occur in the target 
    and hence is tagged as delete

    """
        source_token = source_tokens[min(source_token_idx,
                                         len(source_tokens) - 1)].lower()

        # skip any null tokens
        while (target_token_idx < len(target_tokens) - 1
               and target_tokens[target_token_idx] == "<NULL>"):
            target_token_idx += 1

        target_token = target_tokens[target_token_idx].lower()

        # if a target token doesnt exist in the source tokens
        # it is either a part of the edit vocabulary
        # in case it isnt, the generation is infeasible
        if target_token not in source_tokens[source_token_idx:]:
            if target_token in self._phrase_vocabulary:
                target_tokens[target_token_idx] = "<NULL>"
                return tagging.Tag(
                    "KEEP|" +
                    target_token), target_token_idx + 1, source_token_idx, target_token_idx
            else:
                return 0

        # if source token is in target tokens 
        # return KEEP with the position at which it occurs
        # otherwise tag it as a delete
        elif source_token in target_tokens:
            idx = target_tokens.index(source_token)
            target_tokens[idx] = "<NULL>"
            return tagging.Tag(
                "KEEP|" + str(idx)), target_token_idx, source_token_idx + 1, -1

        else:
            return tagging.Tag(
                "DELETE"), target_token_idx, source_token_idx + 1, -1

    def _find_first_deletion_idx(self, source_token_idx, tags):
        """Finds the start index of a span of deleted tokens.

    If `source_token_idx` is preceded by a span of deleted tokens, finds the
    start index of the span. Otherwise, returns `source_token_idx`.

    Args:
      source_token_idx: Index of the current source token.
      tags: List of tags.

    Returns:
      The index of the first deleted token preceding `source_token_idx` or
      `source_token_idx` if there are no deleted tokens right before it.
    """
        # Backtrack until the beginning of the tag sequence.
        for idx in range(source_token_idx, 0, -1):
            if tags[idx - 1].tag_type != tagging.TagType.DELETE:
                return idx
        return 0


def get_phrase_vocabulary_from_label_map(label_map):
    """Extract the set of all phrases from label map.

  Args:
    label_map: Mapping from tags to tag IDs.

  Returns:
    Set of all phrases appearing in the label map.
  """
    phrase_vocabulary = set()
    for label in label_map.keys():
        tag = tagging.Tag(label)
        if tag.added_phrase:
            phrase_vocabulary.add(tag.added_phrase)
    return phrase_vocabulary
