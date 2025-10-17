import json
import sys
from logging import exception

import stashapi.log as log
from stashapi.stashapp import StashInterface


json_input = json.loads(sys.stdin.read())
FRAGMENT_SERVER = json_input["server_connection"]
stash = StashInterface(FRAGMENT_SERVER)

config = stash.get_configuration()

settings = {
    "appendTags": True
}

if "scenesTagsForMovie" in config["plugins"]:
    settings.update(config["plugins"]["scenesTagsForMovie"])

def update_group_tags(StashGroups: list):

    # Process each movie
    ProcessedMovies = 0
    TotalMovies = len(StashGroups)

    for _Group in StashGroups:

        GroupTags = []
        if settings['appendTags']:
            [GroupTags.append(n.get('id')) for n in _Group['tags']]

        for Scene in _Group['scenes']:

            Tags = stash.find_scene(id=Scene['id'])['tags']
            [GroupTags.append(n.get('id')) if not n.get('id') in GroupTags else None for n in Tags]

        # Update movie with tags from all the scenes
        stash.update_group({
            "id": _Group['id'],
            "tag_ids": GroupTags,
        })

        ProcessedMovies += 1
        progress = ProcessedMovies / TotalMovies
        log.progress(progress)

if __name__ == "__main__":
    if "mode" in json_input["args"]:
        PLUGIN_ARGS = json_input["args"]["mode"]

        if "processGroupTags" in PLUGIN_ARGS:
            update_group_tags(StashGroups=stash.find_groups())

    elif "hookContext" in json_input["args"]:
        Group = json_input["args"]["hookContext"]['input']

        try:
            if Group.get('groups'):

                GroupIds = [stash.find_group({'id': n['group_id']}) for n in Group['groups']]
                update_group_tags(StashGroups=GroupIds)

                log.info(f'Updated tags for group {Group["title"]}')

            else:
                log.info('No groups to update')
        except Exception as ex:
            log.warning(ex)
