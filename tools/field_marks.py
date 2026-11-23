"""Structured field marks for the dichotomous ID key (built into app/data/marks.json).

DRAFT: written from general knowledge and the group tips in confusion_groups.py, NOT yet checked
against a field guide. When you have checked a species against Pizzey & Knight / Morcombe /
Menkhorst, add its name to CHECKED; the app flags keys that still include unchecked species.

How the key uses this
- Each species maps trait -> short value. The app compares values as text (case-insensitive), so
  birds that share a feature must use exactly the same wording ("black", not "black " / "all black").
- Only fill a trait when it helps tell the bird from its look-alikes. A trait that is missing for
  some birds is still usable, but those birds then appear under every branch of that couplet.
- "plumages": {label: {trait: value}} for birds whose sexes or ages look different. Each plumage
  becomes its own entry in the key (e.g. "Superb Fairywren (female)"), with the species-level
  traits as defaults.
- Size is not entered here: the app splits on body length (Garnett 2015) when the gap is clear.

Species names are matched like confusion_groups.py ('Name|Alias' allowed).
"""

# (key, label, tier). Tier 0 = seen on a perched bird, 1 = shape/flight/behaviour, 2 = call/range.
# On equally good splits the key prefers the lower tier, then the earlier trait in this list.
TRAITS = [
    ("bill", "Bill colour", 0),
    ("billShape", "Bill shape", 0),
    ("head", "Head / crown", 0),
    ("face", "Face", 0),
    ("eye", "Eye", 0),
    ("throat", "Throat / neck", 0),
    ("breast", "Breast / underparts", 0),
    ("upper", "Back / upperparts", 0),
    ("wing", "Wing", 0),
    ("rump", "Rump", 0),
    ("tail", "Tail", 0),
    ("legs", "Legs / feet", 0),
    ("shape", "Build", 1),
    ("flight", "In flight", 1),
    ("behaviour", "Behaviour", 1),
    ("call", "Call", 2),
    ("range", "Range / habitat", 2),
]

MARKS = {
    # ---------- Ravens & crows ----------
    "Australian Raven": {
        "throat": "long shaggy hackles, puffed out when calling",
        "call": "slow wailing 'aah-aah-aaaah' with a dying fall",
        "range": "eastern and south-western mainland",
        "head": "grey feather bases (ravens)",
    },
    "Little Raven": {
        "throat": "short hackles",
        "behaviour": "flicks both wings up with each call",
        "call": "deep guttural 'kar-kar-kar'",
        "range": "south-eastern mainland",
        "head": "grey feather bases (ravens)",
    },
    "Forest Raven": {
        "throat": "short hackles",
        "billShape": "very heavy",
        "tail": "short",
        "call": "very deep, slow 'korr-korr-korr'",
        "range": "Tasmania and far south coast",
        "head": "grey feather bases (ravens)",
    },
    "Torresian Crow": {
        "throat": "short hackles",
        "behaviour": "shuffles and re-folds its wings after landing",
        "call": "fast staccato 'uk-uk-uk-uk'",
        "range": "northern and eastern Australia",
        "head": "white feather bases (crows)",
    },
    "Little Crow": {
        "throat": "short hackles",
        "call": "flat nasal 'nark-nark-nark'",
        "range": "inland and western Australia",
        "head": "white feather bases (crows)",
    },

    # ---------- Magpie, currawong, magpie-lark ----------
    "Australian Magpie": {
        "bill": "pale blue-white, black tip",
        "billShape": "strong, straight",
        "eye": "red-brown",
        "head": "black",
        "upper": "white nape and/or back",
    },
    "Pied Currawong": {
        "bill": "black",
        "billShape": "heavy, hooked",
        "eye": "yellow",
        "head": "black",
        "upper": "black",
        "flight": "white tail tip, undertail and wing patch",
    },
    "Magpie-lark|Australian Magpie-lark": {
        "bill": "pale",
        "billShape": "thin",
        "eye": "white",
        "upper": "black and white",
        "behaviour": "walks with a head-bob",
        "plumages": {
            "male": {"head": "black, white eyebrow", "throat": "black"},
            "female": {"head": "black, white forehead", "throat": "white"},
        },
    },

    # ---------- Butcherbirds ----------
    "Pied Butcherbird": {
        "head": "full black hood",
        "throat": "black",
        "upper": "black and white",
    },
    "Grey Butcherbird": {
        "head": "black cap and face only",
        "throat": "white",
        "upper": "grey",
    },

    # ---------- Willie Wagtail / Restless Flycatcher ----------
    "Willie Wagtail": {
        "throat": "black",
        "head": "black, thin white eyebrow",
        "behaviour": "fans tail side to side constantly",
    },
    "Restless Flycatcher": {
        "throat": "white",
        "head": "glossy blue-black cap, no eyebrow",
        "behaviour": "hovers low with a grinding 'scissors' call",
    },

    # ---------- Cuckooshrikes ----------
    "Black-faced Cuckooshrike|Black-faced Cuckoo-shrike": {
        "behaviour": "shuffles wings on landing",
        "plumages": {
            "adult": {"face": "black face", "throat": "black"},
            "juvenile": {"face": "black mask from bill to behind eye", "throat": "grey"},
        },
    },
    "White-bellied Cuckooshrike|White-bellied Cuckoo-shrike": {
        "face": "black mask from bill to behind eye",
        "throat": "grey",
        "behaviour": "shuffles wings on landing",
    },

    # ---------- Miners, myna ----------
    "Common Myna": {
        "head": "all black",
        "face": "yellow bare skin around eye",
        "breast": "chocolate brown",
        "flight": "large white wing patches",
    },
    "Noisy Miner": {
        "head": "black crown",
        "face": "black cheek, yellow skin behind eye",
        "breast": "grey, scalloped",
        "throat": "grey",
        "rump": "grey",
        "flight": "no white wing patches",
    },
    "Yellow-throated Miner": {
        "head": "grey crown",
        "face": "black cheek, yellow skin behind eye",
        "throat": "yellow sides to neck",
        "rump": "white",
    },

    # ---------- Wattlebirds ----------
    "Red Wattlebird": {
        "face": "pinkish-red cheek wattles",
        "breast": "streaked, yellow belly patch",
    },
    "Little Wattlebird": {
        "face": "no wattles",
        "breast": "silver-streaked, no yellow",
        "flight": "rufous wing patch",
    },

    # ---------- New Holland / White-cheeked ----------
    "New Holland Honeyeater": {
        "eye": "white",
        "face": "small white whisker tuft",
    },
    "White-cheeked Honeyeater": {
        "eye": "dark",
        "face": "large white cheek patch",
    },

    # ---------- Big eagles ----------
    "Wedge-tailed Eagle": {
        "tail": "long, wedge-shaped",
        "breast": "dark brown-black",
        "flight": "long fingered wings in a shallow V",
    },
    "White-bellied Sea-Eagle|White-bellied Sea Eagle": {
        "tail": "short, white, wedge-shaped",
        "breast": "white",
        "flight": "wings in a strong V",
        "range": "near water",
    },
    "Little Eagle": {
        "tail": "square, barred",
        "breast": "pale or dark (two morphs)",
        "flight": "pale M-bar on underwing (pale morph)",
    },

    # ---------- Kites ----------
    "Whistling Kite": {
        "tail": "long, rounded",
        "breast": "pale sandy, streaked",
        "flight": "pale M-pattern on underwing, wings slightly drooped",
    },
    "Black Kite": {
        "tail": "forked, constantly twisting",
        "breast": "dark brown",
        "flight": "dark underwing, paler primary bases",
    },
    "Black-shouldered Kite": {
        "flight": "small black patch at wrist under the wing",
        "range": "widespread, open country",
    },
    "Letter-winged Kite": {
        "flight": "long black bar along underwing forming an M/W",
        "range": "inland; often hunts at night",
    },

    # ---------- Accipiters ----------
    "Brown Goshawk": {
        "tail": "rounded tip",
        "face": "heavy brow ('frowning')",
        "legs": "thick",
    },
    "Collared Sparrowhawk": {
        "tail": "square or notched tip",
        "face": "no brow ('staring')",
        "legs": "thin, very long middle toe",
    },

    # ---------- Falcons ----------
    "Peregrine Falcon": {
        "head": "solid black hood",
        "breast": "finely barred",
        "shape": "bulky, broad-chested",
    },
    "Australian Hobby": {
        "head": "dark cap, pale forehead and half-collar",
        "breast": "rufous, streaked",
        "shape": "slim",
    },
    "Brown Falcon": {
        "upper": "brown",
        "face": "double tear-drop cheek mark",
        "behaviour": "hovers clumsily; glides with wings in a shallow V",
    },
    "Nankeen Kestrel|Australian Kestrel": {
        "upper": "pale rufous",
        "face": "thin single tear-drop",
        "behaviour": "hovers steadily and expertly",
    },

    # ---------- Harriers ----------
    "Swamp Harrier": {
        "upper": "dark brown",
        "rump": "white",
        "breast": "buff, streaked",
    },
    "Spotted Harrier": {
        "upper": "grey",
        "rump": "no white",
        "breast": "chestnut with white spots",
        "face": "chestnut",
    },

    # ---------- Owls & frogmouth ----------
    "Southern Boobook|Australian Boobook": {
        "eye": "yellow-green, in dark 'goggles'",
        "billShape": "small, hooked",
        "breast": "brown, pale-spotted",
        "call": "'boo-book'",
    },
    "Barking Owl": {
        "eye": "big, bright yellow",
        "billShape": "small, hooked",
        "breast": "boldly streaked",
        "call": "dog-like 'wook-wook'",
    },
    "Tawny Frogmouth": {
        "eye": "yellow-orange, set to the side",
        "billShape": "huge, wide, frog-like",
        "breast": "grey, finely streaked",
        "behaviour": "perches upright like a broken branch",
        "call": "low pulsing 'oom-oom-oom'",
    },

    # ---------- White cockatoos ----------
    "Little Corella": {
        "bill": "pale",
        "billShape": "short, stubby",
        "face": "small pink patch between bill and eye; blue eye skin",
        "head": "short crest",
    },
    "Long-billed Corella": {
        "bill": "pale",
        "billShape": "long upper tip",
        "face": "red-pink band across face and throat",
        "head": "short crest",
    },
    "Sulphur-crested Cockatoo": {
        "bill": "black",
        "billShape": "large, curved",
        "face": "white bare eye-ring",
        "head": "big yellow crest",
    },

    # ---------- Lorikeets ----------
    "Rainbow Lorikeet": {
        "head": "blue",
        "breast": "orange-red",
        "bill": "red",
    },
    "Scaly-breasted Lorikeet": {
        "head": "green",
        "breast": "green with yellow scaling",
        "bill": "red",
    },
    "Musk Lorikeet": {
        "head": "green, red forehead and ear stripe",
        "breast": "green",
        "bill": "black, tipped red",
    },

    # ---------- Egrets ----------
    "Great Egret|Eastern Great Egret": {
        "bill": "yellow (black when breeding)",
        "face": "gape line extends behind the eye",
        "shape": "very long, kinked neck",
        "legs": "dark",
    },
    "Plumed Egret|Intermediate Egret": {
        "bill": "yellow (black when breeding)",
        "face": "gape line ends below the eye",
        "shape": "medium neck",
        "legs": "dark",
    },
    "Little Egret": {
        "bill": "black",
        "shape": "slim",
        "legs": "black, yellow feet",
    },
    "Eastern Cattle Egret|Cattle Egret": {
        "bill": "yellow, short",
        "shape": "small, stocky, 'jowly' chin",
        "behaviour": "often with livestock",
    },

    # ---------- Cormorants ----------
    "Little Pied Cormorant": {
        "bill": "yellow",
        "billShape": "short, stubby",
        "face": "white face extends above the eye",
        "legs": "white thighs",
    },
    "Australian Pied Cormorant|Pied Cormorant": {
        "bill": "grey",
        "billShape": "long, hooked",
        "face": "yellow-orange skin in front of the eye",
        "legs": "black thighs",
    },
    "Little Black Cormorant": {
        "bill": "grey",
        "billShape": "slim",
        "face": "all black",
        "behaviour": "often fishes in flocks",
    },
    "Great Cormorant": {
        "bill": "grey",
        "billShape": "heavy, hooked",
        "face": "yellow throat skin, white cheek patch",
    },

    # ---------- Grebes ----------
    "Australasian Grebe": {
        "plumages": {
            "breeding": {"head": "black, chestnut neck stripe", "face": "pale yellow spot at base of bill"},
            "non-breeding": {"head": "dark cap to below the eye", "face": "pale yellow spot at base of bill"},
        },
    },
    "Hoary-headed Grebe": {
        "plumages": {
            "breeding": {"head": "black with silvery-white streaks", "face": "no yellow spot"},
            "non-breeding": {"head": "dark cap down to the eye, pale face", "face": "no yellow spot"},
        },
    },

    # ---------- Ducks ----------
    "Pacific Black Duck": {
        "face": "strong dark stripes on a pale face",
        "wing": "green speculum",
        "bill": "dark grey",
    },
    "Mallard": {
        "wing": "blue speculum edged with white",
        "plumages": {
            "male": {"face": "glossy green head", "bill": "yellow"},
            "female": {"face": "plain, single dark eye-line", "bill": "orange and dark"},
        },
    },
    "Grey Teal": {
        "throat": "pale, almost white",
        "face": "plain grey-brown",
    },
    "Chestnut Teal": {
        "plumages": {
            "male": {"face": "glossy green head", "throat": "glossy green", "breast": "chestnut"},
            "female": {"face": "plain, darker brown", "throat": "not obviously pale"},
        },
    },

    # ---------- Coot, moorhen, swamphen ----------
    "Eurasian Coot": {
        "bill": "white",
        "head": "white forehead shield",
        "breast": "sooty black",
        "tail": "dark undertail",
    },
    "Dusky Moorhen": {
        "bill": "red, yellow tip",
        "head": "red forehead shield",
        "breast": "dark grey-brown",
        "tail": "flicks white undertail",
    },
    "Australasian Swamphen": {
        "bill": "red, massive",
        "head": "red forehead shield",
        "breast": "purple-blue",
        "tail": "flicks white undertail",
    },

    # ---------- Ibis & spoonbills ----------
    "Australian White Ibis|Australian Ibis": {
        "head": "black, naked",
        "upper": "white",
        "breast": "white",
    },
    "Straw-necked Ibis": {
        "head": "black, naked",
        "upper": "dark, iridescent",
        "breast": "white, straw-like plumes on breast",
    },
    "Glossy Ibis": {
        "head": "dark, feathered",
        "upper": "dark, glossy",
        "breast": "dark chestnut-brown",
    },
    "Royal Spoonbill": {"bill": "black", "legs": "black"},
    "Yellow-billed Spoonbill": {"bill": "pale yellow", "legs": "pale yellow"},

    # ---------- Shorebirds ----------
    "Bar-tailed Godwit": {
        "billShape": "long, slightly upturned",
        "tail": "barred",
        "flight": "no wing bar",
    },
    "Black-tailed Godwit": {
        "billShape": "long, fairly straight",
        "tail": "black, white rump",
        "flight": "bold white wing bar",
    },
    "Red-necked Stint": {
        "billShape": "short, straight",
        "breast": "plain white (non-breeding)",
        "shape": "tiny, short legs",
    },
    "Curlew Sandpiper": {
        "billShape": "long, down-curved",
        "breast": "plain white (non-breeding)",
        "rump": "white",
        "shape": "long legs",
    },
    "Sharp-tailed Sandpiper": {
        "billShape": "medium, straight",
        "head": "bright rufous cap, pale eyebrow",
        "breast": "streaking fades out gradually",
    },
    "Pectoral Sandpiper": {
        "billShape": "medium, straight",
        "head": "duller brown cap",
        "breast": "streaking ends in a sharp line against white belly",
    },
    "Masked Lapwing": {
        "face": "large yellow wattles",
        "breast": "white",
    },
    "Banded Lapwing": {
        "face": "small red spot above bill, white eye-stripe",
        "breast": "black band",
        "range": "dry open plains",
    },

    # ---------- Gulls & terns ----------
    "Pacific Gull": {
        "bill": "red on both mandible tips",
        "billShape": "enormously deep",
        "tail": "black band (adult)",
        "legs": "yellow",
    },
    "Kelp Gull": {
        "bill": "red spot on lower mandible only",
        "billShape": "slimmer",
        "tail": "all white",
        "legs": "greenish-yellow",
    },
    "Greater Crested Tern|Crested Tern": {"bill": "pale lemon-yellow"},
    "Lesser Crested Tern": {"bill": "orange"},
    "Little Tern": {
        "head": "black line runs right to the bill",
        "bill": "yellow, black tip",
    },
    "Australian Fairy Tern|Fairy Tern": {
        "head": "white gap between cap and bill",
        "bill": "all yellow-orange",
    },

    # ---------- Shearwaters ----------
    "Short-tailed Shearwater": {
        "bill": "dark",
        "tail": "short, toes project past it",
        "wing": "silvery underwing",
    },
    "Wedge-tailed Shearwater": {
        "bill": "dark",
        "tail": "long, wedge-shaped",
        "flight": "buoyant, floppy",
    },
    "Flesh-footed Shearwater": {
        "bill": "pink, dark tip",
        "legs": "pink feet",
        "shape": "large, heavy",
    },

    # ---------- Swallows, martins, swifts ----------
    "Welcome Swallow": {
        "tail": "long forked streamers",
        "rump": "dark",
        "head": "rufous forehead and throat",
    },
    "Tree Martin": {
        "tail": "square",
        "rump": "dull white",
        "head": "dark cap",
    },
    "Fairy Martin": {
        "tail": "square",
        "rump": "bright white",
        "head": "rufous head",
    },
    "White-throated Needletail": {
        "tail": "square",
        "throat": "white",
        "rump": "dark",
        "flight": "white horseshoe under the tail; large, bulky",
    },
    "Pacific Swift|Fork-tailed Swift": {
        "tail": "deeply forked",
        "rump": "white band",
        "flight": "slim",
    },

    # ---------- Pardalotes, thornbills ----------
    "Spotted Pardalote": {
        "head": "black crown with white spots",
        "wing": "black with white spots",
    },
    "Striated Pardalote": {
        "head": "black crown, often finely streaked white",
        "wing": "white stripe with a red or yellow spot at the front",
    },
    "Brown Thornbill": {
        "eye": "red",
        "head": "rufous-scalloped forehead",
        "throat": "streaked",
        "upper": "warm olive-brown",
        "behaviour": "tail usually held level; forages low in shrubs",
        "range": "east and south-east coast, Tasmania",
    },
    "Inland Thornbill": {
        "rump": "rufous",
        "upper": "grey-brown",
        "behaviour": "often cocks its tail",
        "range": "drier inland and west",
    },
    "Striated Thornbill": {
        "head": "rufous crown, finely streaked white",
        "breast": "heavily streaked",
        "upper": "olive-green",
        "behaviour": "usually high in eucalypts",
        "range": "south-east",
    },

    # ---------- Fairy-wrens ----------
    "Superb Fairywren|Superb Fairy-wren": {
        "range": "south-east, incl. Tasmania",
        "plumages": {
            "male": {"head": "pale blue crown and cheek", "throat": "black", "breast": "greyish-white"},
            "female": {"face": "orange-brown around eye and bill", "tail": "brownish", "breast": "pale buff"},
        },
    },
    "Variegated Fairywren|Variegated Fairy-wren": {
        "range": "widespread except far south-east",
        "plumages": {
            "male": {"head": "blue crown and cheek, chestnut shoulders", "throat": "black", "breast": "white"},
            "female": {"face": "chestnut patch in front of eye", "tail": "bluish", "breast": "pale buff"},
        },
    },
    "Splendid Fairywren|Splendid Fairy-wren": {
        "range": "inland and west",
        "plumages": {
            "male": {"head": "all bright blue", "throat": "blue", "breast": "blue with black band"},
            "female": {"face": "brownish-orange around eye", "tail": "blue", "breast": "pale buff"},
        },
    },

    # ---------- Doves & cuckoos ----------
    "Spotted Dove": {
        "throat": "black collar with white spots on back of neck",
        "breast": "pinkish-grey",
    },
    "Laughing Dove": {
        "throat": "speckled bib across upper breast",
        "breast": "pinkish",
        "wing": "blue-grey patch",
    },
    "Fan-tailed Cuckoo": {
        "eye": "yellow eye-ring",
        "breast": "rufous-buff",
        "tail": "notched, white-barred edges",
    },
    "Pallid Cuckoo": {
        "eye": "dark stripe through the eye",
        "breast": "pale grey",
        "head": "white spot on nape",
    },
}

# Species whose marks have been checked against a field guide (by the same names as MARKS).
CHECKED = set()
