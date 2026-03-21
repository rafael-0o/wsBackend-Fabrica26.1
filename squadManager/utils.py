from .rickmorty_client import RickMortyClient
import requests


def enrich_squad_members(members):
    """
    Enriches a list of SquadMember with data from the Rick & Morty API.

    Args:
        members: QuerySet or list of SquadMember

    Returns:
        list: List of dictionaries with 'member' and 'character' keys
    """
    client = RickMortyClient()
    character_ids = [m.character_id for m in members]

    try:
        characters_by_id = client.get_characters(character_ids)
        return [
            {
                "member": member,
                "character": characters_by_id.get(member.character_id),
            }
            for member in members
        ]
    except requests.RequestException:
        # In case of API error, return without character data
        return [
            {
                "member": member,
                "character": None,
            }
            for member in members
        ]