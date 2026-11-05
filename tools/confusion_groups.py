"""Curated Australian confusion groups.

Species names are matched against iNaturalist en-AU common names (or scientific
names). Use 'Name|Alias' when iNat's name may differ. Tips are short field-mark
reminders - check them against a field guide (Pizzey & Knight, Morcombe, etc).
"""

GROUPS = [
    # ---------- Corvids & black-and-white birds ----------
    {"cat": "Black & white", "title": "Ravens & crows",
     "species": ["Australian Raven", "Little Raven", "Forest Raven", "Torresian Crow", "Little Crow"],
     "tips": [
         "Very hard by sight - range and call are the best clues.",
         "Australian Raven: long shaggy throat hackles that puff out when calling; slow, wailing 'aah-aah-aaaah' with a dying fall.",
         "Little Raven: shorter hackles; flicks both wings up with each call; deeper, guttural 'kar-kar-kar'.",
         "Torresian Crow: shuffles/re-folds its wings after landing; fast staccato 'uk-uk-uk-uk'.",
         "Forest Raven: Tasmania and far south; heaviest bill, shortest tail.",
         "Crows have white feather bases, ravens grey - only visible when wind ruffles the neck.",
     ]},
    {"cat": "Black & white", "title": "Magpie, currawong or magpie-lark?",
     "species": ["Australian Magpie", "Pied Currawong", "Magpie-lark|Australian Magpie-lark"],
     "tips": [
         "Australian Magpie: white nape and/or back, red-brown eye, pale blue-white bill.",
         "Pied Currawong: almost all black, yellow eye, heavy hooked black bill; white tail tip, undertail and wing patch show in flight.",
         "Magpie-lark: much smaller and daintier (~27 cm), thin pale bill, white eye; walks with a head-bob.",
     ]},
    {"cat": "Black & white", "title": "Pied vs Grey Butcherbird",
     "species": ["Pied Butcherbird", "Grey Butcherbird"],
     "tips": [
         "Pied: full black hood and bib (black throat).",
         "Grey: white throat, grey back - black only on cap and face.",
     ]},
    {"cat": "Black & white", "title": "Willie Wagtail vs Restless Flycatcher",
     "species": ["Willie Wagtail", "Restless Flycatcher"],
     "tips": [
         "Willie Wagtail: black throat, thin white eyebrow, constantly fans tail side-to-side.",
         "Restless Flycatcher: white throat, glossy blue-black cap; hovers low making a grinding 'scissors' call.",
     ]},
    {"cat": "Black & white", "title": "Cuckooshrikes",
     "species": ["Black-faced Cuckooshrike|Black-faced Cuckoo-shrike", "White-bellied Cuckooshrike|White-bellied Cuckoo-shrike"],
     "tips": [
         "Black-faced: black face AND throat on adults.",
         "White-bellied: black only as a mask from bill to just behind the eye; throat grey. Beware juvenile Black-faced, which also have a small mask.",
         "Both shuffle their wings on landing.",
     ]},

    # ---------- Honeyeaters ----------
    {"cat": "Honeyeaters", "title": "Common Myna vs Noisy Miner",
     "species": ["Common Myna", "Noisy Miner"],
     "tips": [
         "Common Myna (introduced starling): chocolate-brown body, black head, yellow bare skin around eye, big white wing patches in flight.",
         "Noisy Miner (native honeyeater): grey body, black crown and cheek, yellow bill and yellow patch behind the eye.",
     ]},
    {"cat": "Honeyeaters", "title": "Noisy vs Yellow-throated Miner",
     "species": ["Noisy Miner", "Yellow-throated Miner"],
     "tips": [
         "Noisy: black crown.",
         "Yellow-throated: grey crown (no black), yellow sides to the neck, white rump visible in flight.",
     ]},
    {"cat": "Honeyeaters", "title": "Red vs Little Wattlebird",
     "species": ["Red Wattlebird", "Little Wattlebird"],
     "tips": [
         "Red: pinkish-red wattles on cheek, yellow belly patch, larger.",
         "Little: no wattles, silvery streaks on face and body, rufous patch in wing in flight.",
     ]},
    {"cat": "Honeyeaters", "title": "New Holland vs White-cheeked Honeyeater",
     "species": ["New Holland Honeyeater", "White-cheeked Honeyeater"],
     "tips": [
         "New Holland: WHITE eye, small white whisker tuft.",
         "White-cheeked: DARK eye, large white cheek patch.",
     ]},

    # ---------- Raptors ----------
    {"cat": "Raptors", "title": "Big eagles",
     "species": ["Wedge-tailed Eagle", "White-bellied Sea-Eagle|White-bellied Sea Eagle", "Little Eagle"],
     "tips": [
         "Wedge-tailed: huge, long diamond/wedge tail, long 'fingered' wings held in a shallow V.",
         "White-bellied Sea-Eagle: white underbody and head, short white wedge tail, wings in a strong V; near water.",
         "Little Eagle: much smaller (about raven-sized wings), square tail, pale M-shaped bar on underwing (pale morph).",
     ]},
    {"cat": "Raptors", "title": "Whistling vs Black Kite",
     "species": ["Whistling Kite", "Black Kite"],
     "tips": [
         "Whistling: long ROUNDED tail, pale sandy body, wings held slightly drooped; pale underwing pattern.",
         "Black: FORKED tail that twists constantly, dark brown all over.",
     ]},
    {"cat": "Raptors", "title": "Brown Goshawk vs Collared Sparrowhawk",
     "species": ["Brown Goshawk", "Collared Sparrowhawk"],
     "tips": [
         "Tail tip: Goshawk ROUNDED; Sparrowhawk SQUARE or slightly notched.",
         "Sparrowhawk: thin legs, very long thin middle toe, 'staring' face without a heavy brow.",
         "Goshawk: heavy brow ridge (frowning), thicker legs.",
         "Sizes overlap: a female sparrowhawk is about the size of a male goshawk.",
     ]},
    {"cat": "Raptors", "title": "Peregrine vs Australian Hobby",
     "species": ["Peregrine Falcon", "Australian Hobby"],
     "tips": [
         "Peregrine: bulky and broad-chested, solid black hood, finely barred underparts.",
         "Hobby: slimmer, smaller; dark cap with pale forehead and a pale half-collar; rufous-streaked underparts.",
     ]},
    {"cat": "Raptors", "title": "Brown Falcon vs Nankeen Kestrel",
     "species": ["Brown Falcon", "Nankeen Kestrel|Australian Kestrel"],
     "tips": [
         "Kestrel: small, pale rufous back, hovers expertly and steadily.",
         "Brown Falcon: bigger, scruffy brown, double 'tear-drop' cheek mark, long legs; hovers clumsily; glides with wings in a shallow V.",
     ]},
    {"cat": "Raptors", "title": "Black-shouldered vs Letter-winged Kite",
     "species": ["Black-shouldered Kite", "Letter-winged Kite"],
     "tips": [
         "Black-shouldered: only a black patch at the wrist under the wing.",
         "Letter-winged: a long black line along the underwing forming an M/W shape in flight; inland, often nocturnal.",
     ]},
    {"cat": "Raptors", "title": "Swamp vs Spotted Harrier",
     "species": ["Swamp Harrier", "Spotted Harrier"],
     "tips": [
         "Swamp: dark brown above, prominent WHITE rump.",
         "Spotted: grey with chestnut face and white spots on chestnut underparts; barred tail, no white rump.",
     ]},

    # ---------- Owls & nightbirds ----------
    {"cat": "Owls & nightbirds", "title": "Boobook, Barking Owl or Frogmouth?",
     "species": ["Southern Boobook|Australian Boobook", "Barking Owl", "Tawny Frogmouth"],
     "tips": [
         "Southern Boobook: small, dark 'goggles' around yellow-green eyes, spotted brown.",
         "Barking Owl: larger, big bright yellow eyes, streaked breast, no dark goggles.",
         "Tawny Frogmouth: not an owl - huge wide frog-like bill, eyes to the side, perches upright like a broken branch.",
     ]},

    # ---------- Parrots ----------
    {"cat": "Parrots", "title": "White cockatoos & corellas",
     "species": ["Little Corella", "Long-billed Corella", "Sulphur-crested Cockatoo"],
     "tips": [
         "Long-billed Corella: long pale upper bill tip, red-pink band across face and throat.",
         "Little Corella: short stubby bill, bluish bare skin around the eye, small pink patch between bill and eye.",
         "Sulphur-crested: noticeably larger, big yellow crest, black bill.",
     ]},
    {"cat": "Parrots", "title": "Lorikeets",
     "species": ["Rainbow Lorikeet", "Scaly-breasted Lorikeet", "Musk Lorikeet"],
     "tips": [
         "Rainbow: blue head, orange-red breast.",
         "Scaly-breasted: all-green head, yellow scaling on green breast.",
         "Musk: red forehead and red ear stripe, otherwise green; black bill tipped red.",
     ]},

    # ---------- Waterbirds ----------
    {"cat": "Waterbirds", "title": "White egrets",
     "species": ["Great Egret|Eastern Great Egret", "Plumed Egret|Intermediate Egret", "Little Egret", "Eastern Cattle Egret|Cattle Egret"],
     "tips": [
         "Great: very long kinked neck; gape line extends BEHIND the eye.",
         "Plumed (Intermediate): shorter neck; gape line ends below the eye.",
         "Little: slim, BLACK bill, black legs with yellow feet.",
         "Cattle: small and stocky, short yellow bill, 'jowly' chin; often with livestock.",
     ]},
    {"cat": "Waterbirds", "title": "Pied cormorants",
     "species": ["Little Pied Cormorant", "Australian Pied Cormorant|Pied Cormorant"],
     "tips": [
         "Little Pied: small, short stubby yellow bill; white face extends above the eye.",
         "Australian Pied: large, long grey hooked bill, yellow-orange bare skin in front of eye, black thighs.",
     ]},
    {"cat": "Waterbirds", "title": "Black cormorants",
     "species": ["Little Black Cormorant", "Great Cormorant"],
     "tips": [
         "Little Black: all glossy black, slim grey bill, often fishes in flocks.",
         "Great: much larger, yellow throat skin and white cheek patch.",
     ]},
    {"cat": "Waterbirds", "title": "Grebes",
     "species": ["Australasian Grebe", "Hoary-headed Grebe"],
     "tips": [
         "Australasian: pale yellow spot at base of bill; breeding has chestnut neck stripe.",
         "Hoary-headed: breeding has silvery-white streaks on a black head; non-breeding has dark cap down to the eye with pale face.",
     ]},
    {"cat": "Waterbirds", "title": "Pacific Black Duck vs Mallard",
     "species": ["Pacific Black Duck", "Mallard"],
     "tips": [
         "Pacific Black Duck: strong dark face stripes on pale face, green wing speculum, dark bill.",
         "Female Mallard: plain face (one eye line), orange-and-dark bill, blue speculum edged with white. Hybrids are common.",
     ]},
    {"cat": "Waterbirds", "title": "Grey vs Chestnut Teal",
     "species": ["Grey Teal", "Chestnut Teal"],
     "tips": [
         "Grey Teal: pale, almost white throat and lower face.",
         "Female Chestnut Teal: darker overall, throat not obviously pale. Males are chestnut with green heads.",
     ]},
    {"cat": "Waterbirds", "title": "Coot, moorhen or swamphen?",
     "species": ["Eurasian Coot", "Dusky Moorhen", "Australasian Swamphen"],
     "tips": [
         "Coot: white bill and white forehead shield.",
         "Dusky Moorhen: red shield, red bill with yellow tip; flicks white undertail.",
         "Swamphen: much bigger, purple-blue breast, massive red bill.",
     ]},
    {"cat": "Waterbirds", "title": "Ibis",
     "species": ["Australian White Ibis|Australian Ibis", "Straw-necked Ibis", "Glossy Ibis"],
     "tips": [
         "White: white body, black naked head and neck.",
         "Straw-necked: dark iridescent back, white neck/underparts, straw-like plumes on breast.",
         "Glossy: smaller and slimmer, all dark; looks black at a distance.",
     ]},
    {"cat": "Waterbirds", "title": "Spoonbills",
     "species": ["Royal Spoonbill", "Yellow-billed Spoonbill"],
     "tips": ["Royal: black bill and legs.", "Yellow-billed: pale yellow bill and legs."]},

    # ---------- Shorebirds & seabirds ----------
    {"cat": "Shorebirds & seabirds", "title": "Godwits",
     "species": ["Bar-tailed Godwit", "Black-tailed Godwit"],
     "tips": [
         "Black-tailed: in flight, bold white wing bar and white rump with black tail; bill fairly straight.",
         "Bar-tailed: no wing bar, barred tail; bill slightly upturned.",
     ]},
    {"cat": "Shorebirds & seabirds", "title": "Small sandpipers",
     "species": ["Red-necked Stint", "Curlew Sandpiper", "Sharp-tailed Sandpiper"],
     "tips": [
         "Red-necked Stint: tiny, short straight black bill.",
         "Curlew Sandpiper: longer legs, long DOWN-CURVED bill, white rump in flight.",
         "Sharp-tailed: bigger, rufous cap, pale eyebrow, diffusely streaked breast.",
     ]},
    {"cat": "Shorebirds & seabirds", "title": "Sharp-tailed vs Pectoral Sandpiper",
     "species": ["Sharp-tailed Sandpiper", "Pectoral Sandpiper"],
     "tips": [
         "Pectoral: streaked breast ends in a sharp line against a white belly.",
         "Sharp-tailed: streaking fades out gradually; brighter rufous cap.",
     ]},
    {"cat": "Shorebirds & seabirds", "title": "Pacific vs Kelp Gull",
     "species": ["Pacific Gull", "Kelp Gull"],
     "tips": [
         "Pacific: enormously deep bill with red on BOTH mandible tips; black tail band on adults.",
         "Kelp: slimmer bill with red spot on lower mandible only; greenish-yellow legs; all-white tail.",
     ]},
    {"cat": "Shorebirds & seabirds", "title": "Crested terns",
     "species": ["Greater Crested Tern|Crested Tern", "Lesser Crested Tern"],
     "tips": [
         "Greater Crested: larger, pale lemon-yellow bill.",
         "Lesser Crested: smaller, ORANGE bill.",
     ]},
    {"cat": "Shorebirds & seabirds", "title": "Little vs Fairy Tern",
     "species": ["Little Tern", "Australian Fairy Tern|Fairy Tern"],
     "tips": [
         "Little (breeding): black line runs right to the bill; yellow bill with black tip.",
         "Fairy: white gap between black cap and bill; all-yellow-orange bill.",
     ]},
    {"cat": "Shorebirds & seabirds", "title": "Dark shearwaters",
     "species": ["Short-tailed Shearwater", "Wedge-tailed Shearwater", "Flesh-footed Shearwater"],
     "tips": [
         "Short-tailed: smaller, dark bill, toes project past the short tail; silvery underwing.",
         "Wedge-tailed: long wedge tail, buoyant floppy flight; dark bill.",
         "Flesh-footed: larger, heavy PINK bill with dark tip and pink feet.",
     ]},
    {"cat": "Shorebirds & seabirds", "title": "Masked vs Banded Lapwing",
     "species": ["Masked Lapwing", "Banded Lapwing"],
     "tips": [
         "Masked: big yellow facial wattles, white underparts.",
         "Banded: black breast band, small red spot above bill, white eye-stripe; dry open plains.",
     ]},

    # ---------- Small birds ----------
    {"cat": "Small birds", "title": "Swallows & martins",
     "species": ["Welcome Swallow", "Tree Martin", "Fairy Martin"],
     "tips": [
         "Welcome Swallow: long forked tail streamers, rufous throat and forehead.",
         "Tree Martin: square tail, dull white rump, dark cap.",
         "Fairy Martin: rufous head/cap, bright white rump, square tail.",
     ]},
    {"cat": "Small birds", "title": "Swifts",
     "species": ["White-throated Needletail", "Pacific Swift|Fork-tailed Swift"],
     "tips": [
         "Needletail: large, bulky, square tail, white throat and white horseshoe under the tail.",
         "Pacific (Fork-tailed) Swift: slimmer, deeply forked tail, white rump band.",
     ]},
    {"cat": "Small birds", "title": "Pardalotes",
     "species": ["Spotted Pardalote", "Striated Pardalote"],
     "tips": [
         "Spotted: black crown and wings covered in white spots.",
         "Striated: crown black (often fine white streaks), white stripe along the wing with a red or yellow spot at the front.",
     ]},
    {"cat": "Small birds", "title": "Thornbills",
     "species": ["Brown Thornbill", "Inland Thornbill", "Striated Thornbill"],
     "tips": [
         "Brown: red eye, rufous-scalloped forehead, streaked throat.",
         "Inland: often cocks tail, rufous rump, drier country.",
         "Striated: crown finely streaked white on rufous; heavily streaked underparts; usually high in eucalypts.",
     ]},
    {"cat": "Small birds", "title": "Female fairy-wrens",
     "species": ["Superb Fairywren|Superb Fairy-wren", "Variegated Fairywren|Variegated Fairy-wren", "Splendid Fairywren|Splendid Fairy-wren"],
     "tips": [
         "Use the Female filter in the gallery to compare.",
         "Superb female: orange-brown around eye and bill, brownish tail.",
         "Variegated female: chestnut patch in front of eye, bluish tail.",
         "Splendid female: blue tail, brownish-orange face; drier inland/west.",
     ]},

    # ---------- Pigeons & cuckoos ----------
    {"cat": "Pigeons & cuckoos", "title": "Spotted vs Laughing Dove",
     "species": ["Spotted Dove", "Laughing Dove"],
     "tips": [
         "Spotted: black collar on back of neck covered in white spots.",
         "Laughing: smaller, pinkish, speckled bib across the upper breast; blue-grey in wing.",
     ]},
    {"cat": "Pigeons & cuckoos", "title": "Fan-tailed vs Pallid Cuckoo",
     "species": ["Fan-tailed Cuckoo", "Pallid Cuckoo"],
     "tips": [
         "Fan-tailed: yellow eye-ring, rufous-buff breast, notched (white-barred) tail.",
         "Pallid: pale grey, dark stripe through the eye, white spot on nape.",
     ]},
]

# Familiar Australian birds used as rungs on the size ladder (ascending size).
BENCHMARKS = [
    "Superb Fairywren|Superb Fairy-wren", "House Sparrow", "Willie Wagtail", "Common Myna",
    "Rock Pigeon|Rock Dove", "Australian Magpie", "Laughing Kookaburra", "Australian Raven",
    "Pacific Black Duck", "Australian White Ibis|Australian Ibis", "Wedge-tailed Eagle", "Australian Pelican", "Emu",
]
