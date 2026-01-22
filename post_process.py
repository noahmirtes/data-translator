# data_transforms.py

import pandas as pd
from utils import split_tag_list

# ---------------------------------------------- MAIN DATA TRANSFORM FUNCTIONS -----

def copy_by_header(src_df : pd.DataFrame, dest_df : pd.DataFrame, header_map : dict):
    """
    This is the main function that copies the data from the source header to its destination header
    Args:
        src_df : the input data dataframe
        dest_df : the output dataframe with the dest headers
        header_map : the dictionary for the header mapping (source header : dest header)
    """

    for src_header, dest_header in header_map.items():
        try:
            dest_df[dest_header] = src_df[src_header]
        except Exception:
            print(f"Error mapping {src_df} to {dest_header}")

    return dest_df


def run_post_processes(df, transforms):
    """
    transforms = [
        {"func": build_display_title, "params": {"dst": "display_title"}},
        {"func": strip_whitespace, "params": {"cols": ["artist", "title"]}},
    ]
    """
    
    out = df.copy()

    for t in transforms:
        # get the function and args in the registry map
        fn = POST_PROCESS_REGISTRY[t["id"]]
        if not fn:
            print(f"No post process with id {t["id"]} was found.")
            continue
        
        params = t.get("args", {})
        
        # run process
        try:
            out = fn(out, **params)
        except Exception as e:
            print(f"Error runnin post process {t['name']}. Error : {e}")
    return out


# ------------------------------------------------------------- POST PROCESS -----


def strip_illegal_chars(df : pd.DataFrame, headers : str):
    """
    Remove illegal characters from the values in src_header.
    Writes cleaned value to dest_header (or back into src_header if dest_header is None).
    """

    # unchanging, so I just hardcoded it
    illegal_chars = ["\"", "$", "*"]

    def _process(value):
        if pd.isna(value):
            return value

        s = str(value)
        for ch in illegal_chars:
            s = s.replace(ch, "")
        return s.strip()

    for header in headers:
        df[header] = df[header].apply(_process)

    return df


def lowercase(df : pd.DataFrame, headers : str):
    """Converts every string value to a lowercase version of itself"""

    def _process(value):
        if pd.isna(value):
            return value
        
        s = str(value)
        return s.lower()

    for header in headers:
        df[header] = df[header].apply(_process)

    return df




# MAIN TRACK TRANSFORMS

def build_track_title(df, song_title_header, version_header, dest_header):
    def _row(row):
        title = row.get(song_title_header)
        version = row.get(version_header)

        if pd.isna(title) and pd.isna(version):
            return None
        if pd.isna(version):
            return str(title).strip()
        if pd.isna(title):
            return str(version).strip()
        
        # Prevent "Main" as Version
        if version.lower() == "main":
            return f"{str(title).strip()}"
        
        # proper case the version
        version = version.title()

        return f"{str(title).strip()} {str(version).strip()}"

    df[dest_header] = df.apply(_row, axis=1)
    return df

def set_library_id(df, library_id_header, cd_id_header):
    """
    Extracts the text prefix from cd_id_header by removing all digits.
    Writes that prefix into library_id_header.
    Example:
        AMH-0032 -> AMH
        XYZ120   -> XYZ
    """
    def _row(raw):
        if pd.isna(raw):
            return None

        s = str(raw).strip()
        if not s:
            return None

        # Strip digits, leave letters and other non-digit characters
        # If you only want letters, tell me and I'll tighten the rule.
        prefix = ''.join(ch for ch in s if not ch.isdigit()).strip()

        # Optional normalization: uppercase and strip hyphens/spaces
        prefix = prefix.replace("-", "").replace(" ", "").upper()

        return prefix if prefix else None

    df[library_id_header] = df[cd_id_header].apply(_row)
    return df

def set_cd_id(df, cd_id_header):
    """
    Takes values like "AMH 032" or "AMH032" and outputs "AMH-0032".
    Specific to a particular labels input/output format
    """
    def _row(raw):
        if pd.isna(raw):
            return None

        s = str(raw).strip()
        if not s:
            return None

        # Remove spaces and hyphens so we can parse it cleanly
        clean = s.replace(" ", "").replace("-", "")

        # First 3 are prefix, rest is number
        prefix = clean[:3].upper()
        num_part = clean[3:]

        # If numeric part missing or invalid, return prefix only (or None if you prefer)
        if not num_part.isdigit():
            return prefix

        # Zero pad to 4-digit format
        num_part = num_part.zfill(4)

        return f"{prefix}-{num_part}"

    df[cd_id_header] = df[cd_id_header].apply(_row)
    return df


# OTHER CLEANLINESS TRANSFORMS

def strip_illegal_chars(df, strip_header):
    """
    Remove illegal characters from the values in src_header.
    Writes cleaned value to dest_header (or back into src_header if dest_header is None).
    """

    # unchanging, so I just hardcoded it
    illegal_chars = [
        "!", "\"", "$", "(", ")", "*", ",",
        "/", ":", "<", ">", "?", 
        "[", "]", "{", "|", "}", "'"
    ]

    def _clean(value):
        if pd.isna(value):
            return value

        s = str(value)
        for ch in illegal_chars:
            s = s.replace(ch, "")
        return s.strip()

    df[strip_header] = df[strip_header].apply(_clean)
    return df



# MAJOR FACET TRANSFORMS

def filter_instruments(
    df,
    version_header,   # e.g., "Version" or "Track Title"
    instruments_header, # e.g., "Instruments"
    trigger_rules=None,   # list[(list[str] triggers, list[str] removals)]
    require_no_token=" No ",
    exclude_lead_token=" Lead ",
):
    """
    If version contains 'require_no_token' and does NOT contain 'exclude_lead_token',
    then for each (triggers, removals) in trigger_rules:
      - if any trigger is a substring of version, remove all 'removals' from the instrument tags.

    Instruments are expected to be ';' delimited. Output remains ';' delimited.
    """

    def _filter_row(version, instruments):
        # if version/title doesn’t meet gating, do nothing
        if pd.isna(version) or pd.isna(instruments):
            return instruments
        v = str(version)
        if (require_no_token and require_no_token not in v) or (exclude_lead_token and exclude_lead_token in v):
            return instruments

        tags = split_tag_list(instruments)
        if not tags:
            return instruments

        # collect all removals for matched triggers
        to_remove = set()
        for triggers, removals in trigger_rules:
            if any(t in v for t in triggers):
                to_remove.update(removals)

        if not to_remove:
            return instruments

        # preserve order while removing
        kept = [t for t in tags if t not in to_remove]
        return ";".join(kept)


    df[instruments_header] = [
        _filter_row(v, inst)
        for v, inst in zip(df[version_header], df[instruments_header])
    ]

    return df


# FACET EXPANSION

def pad_tags(df, check_headers, map_config):
    """
    Ensure tags found in any of 'check_headers' are also present in target headers
    defined by 'map_config'.

    map_config = [
        (target_header, dictionary_or_iterable_of_valid_tags),
        . . . 
    ]

    Rules:
    - Cells are ';' delimited (no commas).
    - Exact string match (case-sensitive).
    - Keep existing target tags; append missing matches; de-duplicate preserving order.
    """

    def _split_tags(raw):
        if pd.isna(raw):
            return []
        s = str(raw).strip()
        if not s:
            return []
        return [p.strip() for p in s.split(";") if p.strip()]

    # Precompute valid sets per target header
    valid_map = []
    for target_header, dictionary in map_config:
        if isinstance(dictionary, dict):
            valid_map.append((target_header, set(dictionary.values())))
        else:
            valid_map.append((target_header, set(dictionary)))

        # Ensure target column exists
        if target_header not in df.columns:
            df[target_header] = ""

    # Iterate rows
    for idx in df.index:
        # Gather all tags present across check_headers in declared order
        row_tags = []
        seen_row = set()
        for ch in check_headers:
            for t in _split_tags(df.at[idx, ch] if ch in df.columns else None):
                if t not in seen_row:
                    seen_row.add(t)
                    row_tags.append(t)

        if not row_tags:
            continue

        # For each target, append any matching tags not already present
        for target_header, valid in valid_map:
            existing = _split_tags(df.at[idx, target_header])
            seen_out = set(existing)
            out = list(existing)

            for t in row_tags:
                if t in valid and t not in seen_out:
                    seen_out.add(t)
                    out.append(t)

            df.at[idx, target_header] = ";".join(out) if out else ""

    return df

def dedupe_tags(df, dedupe_headers):
    """
    Remove duplicates in semicolon-delimited fields for each header in dedupe_headers.
    Order is preserved. Whitespace is stripped. Empty/null stays empty.
    """

    def _dedupe_cell(raw):
        tags = split_tag_list(raw)
        if not tags:
            return ""
        seen = set()
        out = []
        for t in tags:
            if t not in seen:
                seen.add(t)
                out.append(t)
        return ";".join(out)

    for header in dedupe_headers:
        df[header] = df[header].apply(_dedupe_cell)

    return df

def expand_main_tags_to_alts(df, copy_headers, title_header, type_header):
    """
    If the track type is "Main", copy tags from columns in 'copy_headers'
    to all non-Main rows that share the same 'title_header' value.
    Tags are semicolon-delimited, merged (not overwritten), order-preserving, and de-duplicated.
    """

    def _merge_tags(dest_raw, src_raw):
        dest = split_tag_list(dest_raw)
        src = split_tag_list(src_raw)

        if not src:
            return ";".join(dest) if dest else ""
        
        seen = set(dest)
        out = list(dest)

        for t in src:
            if t not in seen:
                seen.add(t)
                out.append(t)

        return ";".join(out) if out else ""

    # group by title; for each group, find a Main row and propagate to others
    for title, grp in df.groupby(title_header, dropna=False):
        
        # locate a Main row (first occurrence if multiple)
        main_idx = None

        for idx in grp.index:
            v = df.at[idx, type_header]
            if isinstance(v, str) and v.strip().lower() == "main":
                main_idx = idx
                break

        if main_idx is None:
            continue  # no main in this title group

        # for each alt row, merge tags from main across copy_headers
        for idx in grp.index:
            if idx == main_idx:
                continue

            v = df.at[idx, type_header]

            if isinstance(v, str) and v.strip().lower() == "main":
                continue  # skip additional mains, if any

            for col in copy_headers:
                df.at[idx, col] = _merge_tags(df.at[idx, col], df.at[main_idx, col])

    return df



# ------------------------------------------------------------- CONFIGS -----


POST_PROCESS_REGISTRY = {
    1 : strip_illegal_chars,
    2 : lowercase,
    # order your other
}


trigger_rules = [
    (["Vocal", "Instrumental", "Vox"],
        ["Male","Vocal Textures","Female","Synth Voice / Vocoder","Vocal Background","Voice Texture",
        "Chanting, Generic","Human Beatbox","Non Lyric Melody","Treated Vocal","Vocal Phrase / Shout Out","Scat Singing"]),
    (["Brass","Horns"],
        ["Trumpet / Cornet","Brass","Bugle","Flugelhorn","Horn / French Horn","Trombone","Tuba / Sousaphone"]),
    (["Trumpet / Cornet"], ["Trumpet / Cornet"]),
    (["Saxophone"], ["Saxophone","Alto Sax","Baritone Sax","Soprano Sax","Tenor Sax"]),
    (["Drums","Beat"], ["Drum Kit","Drum Machine / Electronic Drums","Drums"]),
    (["Guitar","Electric Guitar","Acoustic","Acoustic Guitar","Dobro"],
        ["Guitar, Electric","Guitar, Acoustic / Nylon String","Guitar, Bottleneck / Slide",
        "Guitar, Distorted Electric","Guitar, Pedal Steel","Guitar, Wah Wah"]),
    (["Acoustic","Acoustic Guitar","Dobro"], ["Guitar, Acoustic / Steel String","Guitar, Dobro"]),
    (["Organ"],
        ["Organ, Barrel","Organ, Bontempi","Organ, Church","Organ, Electric","Organ, Hammond","Organ, Harmonium",
        "Organ, Horror","Organ, Quiz Show","Organ, Stadium","Organ, Wurlitzer"]),
    (["Percussion"], ["Percussion"]),
    (["Mallets","Xylophone","Marimba"], ["Xylophone / Glockenspiel","Vibraphone","Marimba"]),
    (["Keyboard"],
        ["Piano","Piano, Electric","Marimba","Organ, Barrel","Organ, Bontempi","Organ, Church","Organ, Electric",
        "Organ, Hammond","Organ, Harmonium","Organ, Horror","Organ, Quiz Show","Organ, Stadium","Organ, Wurlitzer"]),
    (["Ukulele"], ["Ukulele"]),
    (["Piano"], ["Piano","Piano, Electric"]),
    (["Strings"], ["Cello","Strings","Violin","Viola"]),
    (["Accordion"], ["Accordion / Concertina"]),
    (["Clav","Clavinet"], ["Clavinet"]),
]
