"""Manual review of PhyloPic silhouettes (by image uuid).

FLIGHT: bird drawn in flight - only used if no perched image at that level;
        the app scales these by approximate wingspan instead of body length.
BLOCK:  misleading for Australian relatives (e.g. long ribbon tails) - never used.
"""
FLIGHT = {
    "26c55043-54c5-4d88-9478-1f2073fe5e71",  # Hirundo rustica
    "2cc4c508-2a2e-459d-bcc7-5a40c0ed8ffb",  # Accipiter nisus
    "6e8b1b34-5e81-475a-93d9-0613255964cd",  # Plegadis falcinellus
    "737a0176-deee-4a0f-a721-11534ff2b0c5",  # Apus pallidus
    "7b0a6f36-ffe9-45b7-a095-a5f7a09b9104",  # Ciconia ciconia
    "80d26dd5-8ad7-4917-af3a-d204f04c737a",  # Sterna hirundo
    "b22701ca-d000-4ca4-aa96-b497b15f6f83",  # Fregata magnificens
    "b60fa712-ad3f-4f74-80b0-0b304b28991b",  # Phalaropus lobatus
    "c1d4ec1c-1f61-49c1-8b57-4b4a4e57ac71",  # Pandion haliaetus haliaetus
    "e038a748-825f-4cdc-8909-afe6c29c26fc",  # Hieraaetus pennatus
    "e6c9cf8c-1ac9-4845-920a-307d9d10a61f",  # Hirundapus caudacutus
    "eeb0df66-27ac-4cd9-852d-1af5a1f7679c",  # Pelecanoides
    "092135f1-8faa-4474-89ef-dba54a48c667",  # Hirundo rustica
    "0b8bb50c-de76-4c01-9de8-48862602df98",  # Stercorarius parasiticus
    "0db9dc73-47d8-4357-9366-6d45d5fdb5d7",  # Cecropis daurica
    "15664833-6a30-408b-92e6-03329cce058e",  # Oceanites oceanicus
    "1f3bf322-4ca3-402f-80c9-0260843de5e4",  # Pica pica
    "221a4f65-d161-49ea-b1a8-a7f3a8a7e7cb",  # Ardea alba
    "24aa5bf2-5815-4e7e-a86f-3fcc3af21cc9",  # Hirundapus caudacutus
    "2babc63a-873c-4274-a4c0-2d8d32a09d6d",  # Ciconia ciconia
    "3e6b9118-7aff-4b64-8c95-38b2ee49d922",  # Apus apus
    "4ce73ae2-48e2-40ca-aeae-5c47d7adc047",  # Antigone canadensis
    "5b57af47-7876-4980-8fee-e0d6d3340790",  # Petrochelidon pyrrhonota
    "5d38ae89-8938-427d-ba49-3ae4cde0016c",  # Ardea cinerea
    "63457cae-d0e8-48f9-82e2-869c45034f90",  # Accipiter cooperii
    "665521e1-1a70-465e-9bdb-b67d13ae3661",  # Plegadis falcinellus
    "9bfb8270-43ce-46b9-b2ee-5b3d3baf384a",  # Phalaropus lobatus
    "b0ab7ad7-4888-4a60-b8aa-de2f5147183a",  # Sterna hirundo
    "b738522e-9e29-4f34-9d9c-81215ccf203f",  # Stercorarius pomarinus
    "b828fa30-3190-4198-b304-d6599c1e2ae1",  # Stercorarius longicaudus
    "b961c530-3960-4b4c-89d8-33b48ffaeb9b",  # Falco peregrinus
    "bc4a8806-14e3-454b-8580-7063a5ea76ff",  # Puffinus puffinus
    "bf6989ab-dc1e-4442-8ebb-30f80e4a7e46",  # Daption capense
    "ca85a325-a3e4-4d65-ba6f-77be07f3fd4b",  # Hieraaetus pennatus
    "e1cc6d83-a146-4ba5-b937-c02fc213d6af",  # Fregata magnificens
    "e3afa2d1-8ed6-42b1-a806-04c82b83f4e4",  # Pandion haliaetus
    "e57d083f-9885-4900-90ba-e1e9cf61230a",  # Stercorarius antarcticus
    "f164783d-3bab-45f3-9885-c1b382202369",  # Sterna dougallii
    "f6d52cb8-d89e-467b-af5f-3badaec78112",  # Sterna paradisaea
    "4c93d52f-ce61-49e3-b00d-3b857597a41b",  # Accipiter cooperii
    "0733834b-18e7-4309-b4e4-4f5b6209f5bc",  # Ardea alba
    "0f9d6b91-1a7c-4743-a6d8-64391c25a95c",  # Cygnus columbianus
    "cf38be70-f0a8-4a47-b387-e797ec16c7c1",  # Hirundo rustica
    "b8fd1bd1-2d7b-421b-abf2-45b85b6edfab",  # Falco columbarius
    "4954b737-15d0-4110-a20d-23bc4bee3037",  # Philemon corniculatus
    "60cede88-b9e5-4e2b-b5a7-6c26d027487d",  # Thalasseus bergii
    "6d4428f5-711a-44fc-9036-3062d1a1d1c8",  # Aquila audax
    "8353477c-dc5d-44b6-ab3c-9d0cdf4d64f7",  # Pandion haliaetus
    "0ce6c621-963f-4eba-a419-a1df0b0239be",  # Elanus axillaris
    "d20848dc-7587-4a4e-8abd-3cc69c7a0f23",  # Anas platyrhynchos
    "c2b2d238-e7ff-47b4-b39a-41f8096c087a",  # Petrochelidon pyrrhonota
    "08704377-d7aa-43e0-b66c-23351784239f",  # Antigone canadensis
    "bf5fe2c5-1247-4ed9-93e2-d5af255ec462",  # Jacana spinosa
    "834a54ad-faa8-4242-baf3-0b2e739258e5",  # Hydroprogne caspia
    "ef9c9f12-f20c-470e-845a-8b81c8b3bac5",  # Ciconia
    "088bc660-44e4-4717-b5fc-13ee15ade62b",  # Tyto alba
    "2a94bd08-2911-4173-a6b8-11ec42594b77",  # Falco peregrinus
    "f0ce612c-5986-40ce-b80e-eb9b34a43529",  # Numenius phaeopus
    "3ccd1ac3-ec46-42e7-a646-b35d5b3f32d9",  # Ardeotis kori
    "3d48f0be-6ad5-42e4-adbe-fc7b3e4b8a91",  # Chlidonias niger
    "1bab47d8-d907-48aa-9750-01f8a7e7a077",  # Hieraaetus pennatus
    "8f1a834c-469a-4f21-83a3-247ea3f3f938",  # Ardenna creatopus
    "fd5fd283-2d98-41e0-8639-2e319988c8cc",  # Recurvirostra avosetta
    "5f7d45ec-63e6-4248-bf4b-c1c73fa51016",  # Anous minutus
    "094b703c-e1b6-40ef-a410-1e57de142f57",  # Plegadis falcinellus
    "690eb8a1-96f3-4b13-8f7d-544f8020abf8",  # Hirundapus caudacutus
    "16599233-474a-4c8b-949e-8397421fb7d8",  # Thalassarche cauta cauta
    "cb9921e1-51c1-4f3b-98dd-4ff489c3ba9c",  # Cladorhynchus leucocephalus
    "44dcfdfc-6879-42ef-ae02-8df23a174efd",  # Fregata magnificens
    "06ae006e-1ad5-4f3d-ab40-f6d91ea24a7f",  # Sterna dougallii
    "08ec604f-416d-43c7-b628-e88c9ea1d005",  # Sterna hirundo
    "9171cd2b-3afc-46f4-9ee1-c6515de0378c",  # Phaethon rubricauda
    "deb35243-40b4-42ae-b538-846d72e4ec98",  # Macronectes halli
    "56554944-1a1c-4281-a6e5-49ce2de9b2f4",  # Pterodroma
    "a8ecc1e9-f339-4d85-84c3-aa2fff47b2c1",  # Puffinus griseus
    "82a25ed7-d981-45d1-aa43-9fa4f51129fc",  # Probosciger aterrimus aterrimus
    "deab67d8-46f8-4deb-86c3-78174a32380d",  # Cecropis daurica
    "79bae5f9-a9ad-4fd9-8a4d-1a20d61f59a4",  # Gygis microrhyncha
    "bacf2af3-d5f8-4deb-a3a0-f57898ec0021",  # Pachyptila
    "80976786-565f-4fb5-9081-fabe8d1d685e",  # Apus affinis
    "a8f6073e-dd3a-45b9-b72a-1aaa12d4917f",  # Thalassarche chlororhynchos
    "58005551-049f-497c-912c-db2b5aaec47d",  # Elanus scriptus
    "e7e96370-52a7-4760-9c08-bb7ff6a0ea6d",  # Oceanites
    "0a85aeca-b0a4-4e6f-8770-67c98d56225e",  # Stercorarius antarcticus lonnbergi
    "618c6954-80d7-4bd8-af94-6b49689ab532",  # Cuculus canorus
    "7475dfb2-0d03-4f59-8509-de425542f3c1",  # Sula sula
    "782009b8-e3e8-4cb5-a6a9-a0a06bafa50d",  # Diomedea
    "bc1b9b9b-0f3e-41b4-b342-cf669b69afa1",  # Stercorarius parasiticus
    "d07dcd2b-800a-44ad-9eef-2db5d0e48f15",  # Oceanites oceanicus
    "508804e4-94a7-4a9c-9870-5bc63ee785b5",  # Procellaria aequinoctialis
    "cba92f73-a381-46f3-b452-9039736c4dad",  # Phoebetria palpebrata
    "0df021f0-4bee-4972-8971-ee57a51a5952",  # Daption capense
    "6069d0d3-178d-4f85-b08a-eeb318b6ebdf",  # Phalaropus lobatus
    "b880ac4f-f2da-4c97-b334-1adb3c9b22cf",  # Stercorarius pomarinus
    "d1e7e88d-20fb-4d4c-8a3e-b3417c392291",  # Diomedea exulans
    "cefe26a7-1225-4756-9979-f9063d55911e",  # Phaethon lepturus
    "b9cfa790-1642-49ad-b58c-2e663bc92353",  # Thalassarche chrysostoma
    "376d6d1d-6dae-4658-9aa9-d896f342cd90",  # Pelecanoides urinatrix urinatrix
    "18d7b2f2-6d46-4bb8-be68-aff7dcba617c",  # Sterna paradisaea
    "f830c83d-e32f-41be-8cbe-f29d00326727",  # Pernis apivorus
    "387b6da7-f748-4abb-968a-d0a51e5b4762",  # Fulmarus glacialoides
    "d6668ea1-5914-4b05-abe9-fbc7562f83fc",  # Hydrobates pelagicus
    "46def709-d426-4367-a27e-49a9999d0297",  # Stercorarius longicaudus
    "ee53cc23-ecf6-4867-8f2d-4f55286efdd1",  # Pseudobulweria aterrima
    "25cbb3aa-3f66-4ab1-912e-e42f4a2e4af2",  # Falco subbuteo
    "2055bc65-ed8a-462c-ac3f-976dac3db211",  # Pterodroma baraui
    "248a86e6-f8f8-46ea-8147-56bcb0cdd465",  # Ardeola grayii
    "4405e154-34c5-42df-a996-fc8329b08c34",  # Pica hudsonia
}

BLOCK = {
    "38e8ab0b-9010-4b9f-a4a5-39a06f7b346b",  # Ardea alba
    "5ff31c14-a043-4d0e-afe6-8f24cabcf5a7",  # Anhinga rufa
    "6f21e1fa-64c4-4a19-bce6-a8081dcab188",  # Puffinus puffinus
    "30f0acf2-fee7-483d-ac20-a06021c34009",  # Anhinga anhinga
    "c3207abb-94c3-4bd6-9f16-d8b76a49af29",  # Morus sectator
    "eaaf2b20-bf4a-485e-8dc5-751f00638011",  # Diphyllodes respublica
    "f93dc0d8-b9ff-41fb-b393-7c9d81a64fe9",  # Caprimulgus vexillarius
    "87d6a89a-9044-49cd-b708-086c847735f2",  # Terpsiphone paradisi
    "2b7e0e94-c200-4cfa-9074-e5829e5899e1",  # Anhinga anhinga
    "725bea68-c647-4220-829b-f4e5fc8c097c",  # Aechmophorus occidentalis
    "dece9524-b81b-4ed7-b04d-248a496edec5",  # Morus bassanus
    "a83f8fb0-e8ca-44e4-8802-15b4c25c519e",  # Caprimulgus vexillarius
    "bf5f3595-2fd1-4bbe-808c-e2a6b89fd192",  # Astrapia mayeri
    "e1c65be8-50ea-4c7f-9e92-d848f238ef13",  # Enicurus schistaceus
    "2928641d-32f3-4543-889e-dd891c1a7783",  # Pavo muticus
}

# Reviewed and fine (perched/standing/swimming). Preferred over unreviewed images.
PERCHED = {
    "312dcb35-7b82-4496-9db5-2bf7de55e810",  # Acanthorhynchus tenuirostris
    "7ae5a12e-85ea-4395-9529-de821b92f74c",  # Agapornis roseicollis
    "ac6920cc-61a3-4d33-86b6-e8da07011f87",  # Strepera graculina
    "2236b809-b54a-45a2-932f-47b2ca4b8b7e",  # Cacatua sulphurea
    "1ad0e342-c215-4a51-957b-4f556e6efe11",  # Amytornis ballarae
    "52adef9e-6d59-46e8-9c3e-7fc593c55a42",  # Malurus cyaneus
    "3d079e05-45ea-4790-813e-780ef05a93ee",  # Anas (crecca)
    "d708f0e9-1e19-4507-8576-a1e0c870a42c",  # Acanthiza lineata
    "35afd1db-6ff2-42fa-a192-edd039c0cd0c",  # Rhipidura albiscapa
    "b7e062b8-004d-4db6-8211-6257415f0661",  # Caloenas nicobarica
    "1a0320d5-2384-40f4-943a-111273db93b6",  # Dacelo novaeguineae
    "c961d79e-eeba-40c1-a4da-f93f22b264c7",  # Petroicidae
    "ca77f63b-1be7-4f99-a494-2dc1cf3fd301",  # Egretta garzetta nigripes
    "dc45103f-fbd1-427d-b4a7-0f02f3af2417",  # Chenonetta jubata
    "b5a6d49e-e78c-46b4-a2e4-d246a3f4c5d8",  # Anthochaera carunculata
    "3958c728-143c-40a5-804b-f8f30cda584a",  # Coturnicops noveboracensis
    "21a3420c-8d7a-4bd2-8ff7-b89fe7f5add5",  # Phalacrocorax carbo
    "0814fc4b-fdd4-472d-b1bb-a602f1303708",  # Threskiornis molucca
    "38864274-89b7-4a09-a1e1-5f9eb08327f5",  # Chroicocephalus novaehollandiae
    "1f365015-ceb0-4be8-b35f-5be7dacce0cb",  # Podargus strigoides
    "1a956443-14d1-486e-bbbd-39dc40e31eef",  # Vanellus chilensis
    "097958fc-bb7c-4bd8-a2fb-9764a388ac10",  # Microcarbo niger
    "2a168f51-4016-4a32-ba72-64a53bee31ca",  # Pelecanus
    "3058ef80-f441-4ded-a0a1-85f2fce60ce6",  # Estrilda
    "c3551df6-2dfc-4b84-b8b3-aa59fbb272bd",  # Gallinula chloropus
    "828b7d15-d69f-4773-99c5-9eb571d8db19",  # Alectura lathami
    "ec8aefb9-d35f-4fe2-9fec-b3b38d253853",  # Coccyzus americanus
    "e8addae2-efd7-44e7-8544-9a84ff9e4b31",  # Alisterus scapularis
    "6209c9be-060e-4d7f-bc74-a75f3ccf4629",  # Alcedinidae
    "1042852a-ac13-4679-8d57-c31c2dce8513",  # Corvus
    "53f6ce59-911e-4786-903a-d0db267712b4",  # Pericrocotus flammeus
    "5aaa4378-de29-4a20-bdaa-41a8b9b7ad54",  # Fulica atra
    "c3c19b65-cb8d-40bd-b1a6-82a3277bcd4f",  # Sericulus
    "792aade7-560e-4d73-8f53-7b8a4ee5ed14",  # Oriolus auratus
    "65ed3e2d-38f5-421f-976c-be4df6ac73fa",  # Haematopus longirostris
    "f6a0f75e-efc3-43c4-a91b-9b988311886f",  # Pardalotidae
    "9e544c62-ff98-4bc1-81f3-7f144ec33c0a",  # Anser brachyrhynchus × indicus
    "052170eb-17fe-4d51-9ef8-e79346f6a729",  # Platalea ajaja
    "2f44f634-713c-42dc-af7d-6dc8e88470b5",  # Spilopelia chinensis
    "9d382526-f8be-457a-b97d-f323a146b42a",  # Zosterops
    "26ebcc3d-4cbe-4a3b-8ab0-74315d438849",  # Phaps chalcoptera
    "310b4994-af54-4d7b-93ac-27bbf80f7706",  # Columba livia
    "88e81763-9f33-4854-8003-477550932a38",  # Ptilotula penicillata
    "cc7d35ad-fcab-47d5-8a63-2930bd128891",  # Tachybaptus ruficollis
    "b853c7c8-05ba-4f0e-a9ee-5ba7786b5b3e",  # Burhinus oedicnemus
    "8190dab1-09e7-44ca-8b64-87292a9323b9",  # Acridotheres fuscus
    "e95617cf-d73d-46c7-95b0-0c8b64179d1a",  # Entomyzon cyanotis
    "04974d78-9b2c-4011-ba96-5c79e6d49bc5",  # Ninox strenua
    "e66d17b1-2c95-42a6-b6dc-9df4513c6601",  # Climacteris
    "37df7041-de35-461d-bf1a-aec5b6f6ba8b",  # Merops apiaster
    "fcc02884-41c9-4fb8-a766-1c42874ad0e6",  # Calidris alba
    "3d38baad-d355-432a-944c-07608828d0a4",  # Corcorax melanorhamphos
    "22dec87a-4b5c-4320-8848-f9e45462de10",  # Threskiornis spinicollis
    "fcc3ea71-17d5-44cc-8b52-dea48a83c943",  # Anarhynchus nivosus
    "cdc32ece-706b-41d0-8145-6ccfe4a45b9f",  # Thinornis cucullatus
    "bae88982-352f-43d0-b2ed-8d7661fa1d6f",  # Dromaius novaehollandiae
    "2eeef6a6-55c4-4bb6-843f-a11e634d386e",  # Himantopus leucocephalus
    "35f902d0-c82d-40d5-8c9b-42a76223edc2",  # Larus
    "d5194798-0b50-4a79-8b3d-e6efe468c5ab",  # Gallirallus australis
    "168e2b11-a1e0-47d2-b386-c456c879c8d5",  # Aythya affinis
    "3a4cdd72-e553-40ad-838e-3b23037b2010",  # Passer domesticus
    "ec11f62e-ed3e-49bb-bcff-4e47b281d378",  # Turdus merula
    "92cf311d-e7d3-488a-84e7-afe701c161a6",  # Milvus migrans
    "cbb965de-4727-43a2-a6fa-868d57f8afd6",  # Sturnus vulgaris
    "fb4a4bb7-a50f-4d84-9365-5b25638468e6",  # Nycticorax
    "69c936f5-7ed7-4c72-9081-ac860f1e89d1",  # Dicrurus leucophaeus
    "94b3f85c-02aa-4129-a5d3-9b7293c9400a",  # Menura novaehollandiae
    "e470e9bc-869f-46f7-885a-cac1dc724b32",  # Anseranas semipalmata
    "868634a9-3907-46cb-863f-dc70b1599a53",  # Tadorna
    "76e7ec55-7205-49ef-85f7-fd842350306c",  # Dendrocygna viduata
    "a6a38d55-71be-43f2-b781-9a845662de20",  # Limosa lapponica
    "f1d0803e-00d6-41e8-bc67-41c69c7fd946",  # Dicaeum aureolimbatum
    "e1d2cf2f-76cd-4c19-ba5b-c1f5abd841b8",  # Acrocephalus palustris
    "54314e14-cfce-485b-8ad6-571df08824d6",  # Anthus rufulus rufulus
    "66d6bcf5-e08c-4d0d-bd3c-3afa13ba5e28",  # Locustella naevia
    "6bfbc362-431b-441c-8186-4e4b9fa92d08",  # Tringa brevipes
    "c3cc09c4-0fe6-49d3-814e-8f4395c0424d",  # Ceyx fallax
    "5c60ddac-1d35-498e-9556-d80cf137d944",  # Circus hudsonius
    "76448840-ad3d-48df-aaad-19383c17c552",  # Butorides virescens
    "09938c03-f830-4552-a047-ea60e72cb9a8",  # Cisticolinae
    "b6d99569-4221-418c-bf3c-684e2dc2b00c",  # Aepypodius bruijnii
    "8a92c6a5-64fe-4108-a7cf-c32c0f3407e8",  # Catharus
    "7bf8ca33-0fef-4985-a4d4-a147bff6e98c",  # Taeniopygia guttata
    "6ace6a58-7532-4dd9-a218-a148ab09e0be",  # Aethopyga siparaja
    "deba1d91-daa8-40a6-8d48-7a9f295bc662",  # Podiceps cristatus
    "73406cde-c792-45d4-b742-2bb82d46e6eb",  # Lonchura punctulata
    "086d2b94-f13c-47ab-9538-c9b71d97f934",  # Coracias caudata
    "e57b0bc2-7940-401b-b7ca-7e4a5e201c9e",  # Smicrornis brevirostris
    "3644ff17-3cd1-4c98-afdb-91113d4e2cca",  # Columba
    "b3f43d07-a214-4859-82fc-7eec69eeb6fe",  # Numenius madagascariensis
    "5d98a9de-a9e5-49d6-8ed2-cc0c439b3ac8",  # Oxyura jamaicensis
    "00cccd9b-0cd7-4677-9918-eddeac5cf1c6",  # Eudyptula minor
    "0fb8f5c4-3191-4bb8-a5aa-c1cb3fe17eb2",  # Carduelis carduelis
    "6fe53db2-831d-47c4-84db-34b7b429cc40",  # Casuarius casuarius
    "d7c59a44-774f-4191-8623-07c77ca77851",  # Larus dominicanus
    "a861cc3b-4940-4b80-84d7-5d1b07ba6a28",  # Pluvialis squatarola
    "a0749880-ad97-4d31-a8a6-26fa3268b758",  # Geophaps plumifera
    "cdecce9e-84dd-4188-8d71-ca4f55834412",  # Synoicus chinensis
    "16c51a06-21bd-4e34-9f71-d7eea73124d8",  # Arenaria interpres
    "5e338b5b-0f48-4bf6-b737-90b12876a49b",  # Anser (Anser)
    "416ec8c6-0ed1-4c9f-b4a4-8c1ef6496e84",  # Turnix sylvaticus lepurana
    "1c755e3f-0211-4222-942b-ac2f4aaf364f",  # Pitta moluccensis
    "3b3dcd4b-9ba3-4fc9-8eca-570fda3f96d2",  # Cairina moschata
    "fba21da5-0dc4-44d0-a5ac-a9a2e024f46f",  # Gallinago gallinago
    "5e4a8214-5fd2-4a9e-adcc-3ff2fc23aaf9",  # Ptiloris victoriae
    "9e9780c0-baaf-4c83-a2d5-58c62a62135e",  # Actitis hypoleucos
    "b99fb786-7aa3-4344-aa41-eee1dbca1186",  # Aegotheles cristatus
    "93400ea7-5b4c-4d5f-92ae-2345f228df08",  # Melopsittacus undulatus
    "631543cd-0e41-43b6-a325-335a06b2045e",  # Pavo cristatus
    "fcde8660-84a2-43d2-b8f5-90a2de9f0f7d",  # Nymphicus hollandicus
    "217b650d-edaa-4f21-ac5d-03908fd5eac4",  # Menura
    "12929bbe-e83e-472b-83ef-00f5ef7c2b32",  # Ptilinopus arcanus
    "2898c1c6-aa12-4c55-a70c-bdd25ab5df27",  # Corvus tasmanicus
    "f7200232-d635-4d79-bcaa-a59867376d09",  # Numida meleagris
    "d06311f8-eacf-47bb-b3ff-29c7ec1d86c7",  # Pycnonotus leucogenis
    "8ddf3f37-2e1e-40d7-b7d6-0458e71f4b50",  # Alauda arvensis
    "fe44872c-8255-4ec0-8952-209fecb6647c",  # Sula granti
    "f6acc01b-3de7-4428-b503-e12343418c7a",  # Leipoa ocellata
    "68833b6a-dd41-41c9-93e0-37cfa5619e68",  # Antrostomus saturatus
    "8cec794d-6310-4ead-927c-5994dd487270",  # Glareola isabella
    "0580ee17-1897-4e87-ad2e-0644a36cdce8",  # Chloris chloris
    "2de1c95c-7e1f-429b-9c08-17f0a27d176f",  # Gallus gallus domesticus
    "8df99626-e447-4b1b-928f-fe5dc3b7bd1f",  # Calidris canutus
    "e0a19491-63a1-4f09-9eea-7a755d8d2f83",  # Coturnix coturnix
    "1fda4a62-111c-4e4c-9e12-ac0da0656cd9",  # Limosa limosa
    "53514ca9-3c7f-4ec6-bd3e-fd853ac4ac13",  # Amazilia
    "8425d5c7-e62d-4fd2-9a33-82ae4ef83251",  # Thalassarche melanophris
    "396fd6fe-05b5-4289-8f29-315db6c83a35",  # Thalasseus maximus
    "e43fcbd5-4d9f-40ca-8d75-af4ca72260dd",  # Pedionomus torquatus
    "cbacc780-58ef-4a04-98e3-c1c66c25d290",  # Psittacula alexandri
    "f1f4ad6a-c11b-46e1-9f01-7a325d1b7bc5",  # Eudyptes chrysocome filholi
    "21c50828-58d8-42df-9219-2c1b0fb57c99",  # Aptenodytes patagonicus
    "1f13537d-6c37-4179-a127-710218b97072",  # Passer montanus
    "a9ea8058-61c9-4c1f-811c-1345e53e53a0",  # Pezoporus occidentalis
    "ca42294f-afc5-40a0-b14b-fd81c5b5557d",  # Streptopelia decaocto
    "f4327bb3-76b9-4f60-b407-45e2c9ac602b",  # Motacilla alba
    "3505388e-32ed-464d-816a-0bfca1b68934",  # Meleagris gallopavo
    "3813ebf5-b823-4f08-b05c-076fa09426e5",  # Calidris pugnax
    "e5927edf-bc35-4558-9109-e705772d7ab1",  # Amytornis goyderi
    "86334821-42ec-4da1-bb9d-53f3d6941c77",  # Pygoscelis papua
    "e40adfe7-6dc5-426b-9b50-aa02b033db6d",  # Turdus philomelos
    "05cd7d8c-6b2c-4b97-b7b8-053559019eeb",  # Cygnus olor
    "8b720ff5-8e5a-4640-babc-cc30d6495a84",  # Phasianus colchicus
    "225d7ce6-b4e8-4f71-be3b-3d5aa2059078",  # Leucocarbo atriceps
    "31789d9c-30e0-4f40-8c21-6f76cd5d339b",  # Struthio camelus
    "14269801-89fe-405c-a425-2286c54ee60d",  # Arborophila hyperythra
    "91973860-8980-4c6f-a146-58ff0cf33cf7",  # Limosa haemastica
    "ef6d1b7a-15fe-46cc-aa1e-2598d767895c",  # Calidris fuscicollis
    "8e28f15f-6551-40a7-ab5d-668b4e2a585c",  # Leucophaeus atricilla
    "be215386-95b3-4477-a657-cbf0d7b6d669",  # Corvus splendens
    "8e624402-5e75-4f02-bc94-36fa8a6b4929",  # Charadrius semipalmatus
    "e4bbf935-366e-4e20-a6f2-4a0465f9b7df",  # Chroicocephalus ridibundus
    "85bdbe81-9c4f-49ab-a75b-f8b621a9d28e",  # Coturnix japonica
    "b7082743-8119-4baa-b005-77f67a25405a",  # Ara ararauna
    "ad11bfb7-4ab8-47d2-8e25-0e11ab947e20",  # Threskiornis aethiopicus
    "910114e1-39c6-4eae-87d5-fd702dc47161",  # Numenius arquata
    "4e4df08e-d11a-4250-869c-44ce8ab72dd7",  # Phoebetria fusca
    "07a8ddc3-6440-4ca8-80e6-ccdaa988a968",  # Amazona aestiva
    "2d6bb997-f674-4c71-8272-90a398795fb0",  # Thalassarche salvini
    "48053987-63c1-47bc-87c3-2abf84480a6f",  # Callipepla californica
    "1c9fb51b-5615-40fb-a2a8-f201fd61ac02",  # Tringa flavipes
    "a1bb78e7-0657-4189-ab31-8c2a3798fbae",  # Aix galericulata
    "0d19238f-25ca-42a5-a1e2-d108defb75f1",  # Ara macao
    "0ce048be-81f6-43e1-9099-578b4037526f",  # Alopochen aegyptiaca
    "39ed6de3-8b5d-469f-b360-e55f537ebda1",  # Colinus virginianus
    "24304b48-6a05-48bf-97f9-b2a7a7814363",  # Calidris bairdii
    "48080c33-13b8-40e7-8959-1bda598a61b6",  # Anas acuta
    "16bf1400-b7a0-4a1c-a64d-0a9eed116080",  # Branta canadensis
    "92e5161b-2f0b-4675-beea-5484a9b51788",  # Oenanthe hispanica
    "6b0fa335-3b7c-404a-a333-5c3c20ad386b",  # Muscicapa striata
    "0e752edb-ec92-4f5e-b988-2b22566a196e",  # Anodorhynchus hyacinthinus
    "2d15ad88-a76c-4831-a1d4-9fab422f1a7b",  # Aratinga solstitialis
    "d791cad7-c2bc-41ed-9ec2-d49e0e3152bb",  # Psittacus erithacus
    "b217ad1b-0669-4666-80da-9ddc3c3506e2",  # Upupa epops
    "fe052072-ca79-40fc-a38f-ab3418badd93",  # Pygoscelis antarcticus
    "b6499f78-a3f4-4a5b-8370-f3b70b942333",  # Mareca penelope
    "2135a41e-5d1d-454f-9f72-d86892d3d6a8",  # Podiceps auritus
    "3266d069-f33e-4f80-9d0a-d8b0fddd1fe2",  # Recurvirostra avosetta
    "3ceaa22b-8879-4545-9e32-425010f33cd4",  # Anas platyrhynchos
    "5672d2a9-8f5f-449c-a6dd-ba4ebe3f768b",  # Tyto alba
    "6dac57de-2f58-4b72-a1f7-dbeea0e45948",  # Anous minutus worcesteri
    "915910e5-ee4b-4588-9381-2b296fd46df6",  # Probosciger aterrimus aterrimus
    "990d0a0b-0649-4ea6-bc54-662bb599acae",  # Chlidonias niger
    "b0420177-022d-4386-8bac-ba23fbdad6c6",  # Cygnus columbianus
    "b0d54194-4105-4694-b670-b693df1640cf",  # Erithacus rubecula
    "b46a2d4a-d45f-4d7b-b243-9da2c7153f2b",  # Ardeotis kori
    "cc0d5188-fe9e-4963-913f-97668d3deb47",  # Aquila audax
    "ff9e1c92-158a-49ad-80f7-ca10919452fb",  # Philemon corniculatus
    "19899811-afff-4ba8-8084-cc7fe762da7e",  # Caprimulgus
    "1d5f26b6-4a9a-48ad-b799-a83eadb078ca",  # Falco peregrinus peregrinus
    "68432129-405e-460a-ab56-8dc9286f4baf",  # Pica hudsonia
    "7f02b605-c87b-4ec2-9e14-011f813c23a4",  # Antigone canadensis
    "c2d57ce4-0df4-4884-bb5b-f52c71f83b29",  # Manucodia comrii
    "f7b6e10d-ca21-48a2-9fff-d64ebaa046a7",  # Morus sectator
}
