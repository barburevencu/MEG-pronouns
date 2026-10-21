# Image prompts for the people nouns

One prompt per image. Each prompt is self-contained: paste it whole, and attach
the reference picture (the police officer) every time, so the model copies its
style, framing and lighting. Start a new chat for each image so earlier images
don't bleed into the next face.

## How the set is balanced

Gender follows the noun: the 8 masculine nouns get men, the 8 feminine nouns get
women. Within each gender, the faces are 2 White European, 2 Black, 1 East Asian,
1 South Asian, 1 North African / Middle Eastern, 1 Latin American. The pairings
avoid the obvious stereotypes (no East Asian seamstress, no South Asian or North
African driver, no Black singer, no minority-only low-status jobs). Ages run from
mid-20s to mid-50s, and each face has its own shape, hair and features.

What identifies each job: the uniform alone where that is enough, otherwise the
uniform plus objects held in the hands. No furniture, no vehicles, no text or
logos in any image.

| Noun | Person | Uniform only | + held objects |
|---|---|---|---|
| marin | Latin American man, 30s | ✔ | |
| facteur | Black man, 40s | | mailbag, blank envelopes |
| bûcheron | South Asian man, 30s | | axe |
| plongeur | White man, 20s | ✔ | |
| bijoutier | Black man, 50s | | loupe, diamond ring, velvet tray of rings |
| chauffeur | White man, 50s | | car key, umbrella |
| menuisier | North African man, 40s | | hand plane, wooden plank |
| mécanicien | East Asian man, 30s | | wrench |
| nonne | White woman, 40s | ✔ | |
| bergère | White woman, 50s | | shepherd's crook, raw wool fleece |
| danseuse | Black woman, 20s | ✔ | |
| serveuse | South Asian woman, 30s | | tray with coffee |
| caissière | East Asian woman, 20s | | barcode scanner aimed at a bag of apples with a barcode |
| chanteuse | North African woman, 30s | | handheld microphone |
| coiffeuse | Latin American woman, 40s | | scissors, comb, hairdryer |
| couturière | Black woman, 50s | | tape measure, pincushion, shears, pinned fabric |

`plongeur` is drawn as a diver, not a dishwasher.

---

## Shared style block (already included in every prompt below)

> Photorealistic studio photograph, matching the attached reference image exactly
> in style, framing and lighting. Square 1:1 image. One adult person, full body
> from the top of the head to the soles of the shoes, centred, standing upright and
> facing the camera squarely, feet slightly apart, weight on both feet, body taking
> up about 85% of the image height with a small margin above the head and below
> the feet. Camera at chest height, straight on, no tilt, no wide-angle distortion.
> Calm, neutral expression with a closed mouth, looking straight into the lens.
> Plain, seamless, light-grey studio background and floor, no horizon line, no
> scenery. Soft, even, diffuse front lighting with only a faint contact shadow under
> the feet. Sharp focus on the whole figure. Absolutely no text, letters, numbers,
> logos, brand names, labels, stickers, price tags, name tags, printed or
> embroidered patches, flags or insignia anywhere in the image: every garment and
> every object is plain and unbranded. No furniture of any kind (no tables,
> counters, desks, chairs, stools, benches, shelves) and no vehicles; the person
> stands alone and everything that identifies the job is worn or held. No other
> people. Realistic, clean, ordinary-looking clothes and objects, not
> a costume, not stylised, not a cartoon, no dramatic pose.

---

## marin

```text
Photorealistic studio photograph, matching the attached reference image exactly in style, framing and lighting. Square 1:1 image. One adult person, full body from the top of the head to the soles of the shoes, centred, standing upright and facing the camera squarely, feet slightly apart, weight on both feet, body taking up about 85% of the image height with a small margin above the head and below the feet. Camera at chest height, straight on, no tilt, no wide-angle distortion. Calm, neutral expression with a closed mouth, looking straight into the lens. Plain, seamless, light-grey studio background and floor, no horizon line, no scenery. Soft, even, diffuse front lighting with only a faint contact shadow under the feet. Sharp focus on the whole figure. Absolutely no text, letters, numbers, logos, brand names, labels, stickers, price tags, name tags, printed or embroidered patches, flags or insignia anywhere in the image: every garment and every object is plain and unbranded. No furniture of any kind (no tables, counters, desks, chairs, stools, benches, shelves) and no vehicles; the person stands alone and everything that identifies the job is worn or held. No other people. Realistic, clean, ordinary-looking clothes and objects, not a costume, not stylised, not a cartoon, no dramatic pose.

The person: a Latin American man in his early 30s, medium-brown skin, oval face, short black wavy hair, neatly trimmed short black moustache and no beard, dark brown eyes, slim athletic build.

The profession must be recognisable from the uniform alone: he is a navy sailor in a traditional white sailor uniform — white jumper with a wide navy-blue square sailor collar with white stripes at the back, a black neckerchief tied at the chest, white bell-bottom trousers, black polished shoes, and a round white sailor cap with a small red pompom on top. Arms relaxed by his sides. No objects in his hands, no furniture.
```

## facteur

```text
Photorealistic studio photograph, matching the attached reference image exactly in style, framing and lighting. Square 1:1 image. One adult person, full body from the top of the head to the soles of the shoes, centred, standing upright and facing the camera squarely, feet slightly apart, weight on both feet, body taking up about 85% of the image height with a small margin above the head and below the feet. Camera at chest height, straight on, no tilt, no wide-angle distortion. Calm, neutral expression with a closed mouth, looking straight into the lens. Plain, seamless, light-grey studio background and floor, no horizon line, no scenery. Soft, even, diffuse front lighting with only a faint contact shadow under the feet. Sharp focus on the whole figure. Absolutely no text, letters, numbers, logos, brand names, labels, stickers, price tags, name tags, printed or embroidered patches, flags or insignia anywhere in the image: every garment and every object is plain and unbranded. No furniture of any kind (no tables, counters, desks, chairs, stools, benches, shelves) and no vehicles; the person stands alone and everything that identifies the job is worn or held. No other people. Realistic, clean, ordinary-looking clothes and objects, not a costume, not stylised, not a cartoon, no dramatic pose.

The person: a Black man in his mid 40s, dark brown skin, broad round face, close-cropped greying black hair, short salt-and-pepper beard, medium sturdy build.

He is a postman (mail carrier): light-blue short-sleeved uniform shirt, dark-navy trousers, black walking shoes, a navy-blue cap. To make the job unmistakable he carries a large brown leather mail satchel on a strap across his body, its flap open and full of white envelopes, and holds a small bundle of white envelopes in his right hand at waist height. Left arm relaxed. The envelopes are blank, with no writing or stamps. No furniture.
```

## bûcheron

```text
Photorealistic studio photograph, matching the attached reference image exactly in style, framing and lighting. Square 1:1 image. One adult person, full body from the top of the head to the soles of the shoes, centred, standing upright and facing the camera squarely, feet slightly apart, weight on both feet, body taking up about 85% of the image height with a small margin above the head and below the feet. Camera at chest height, straight on, no tilt, no wide-angle distortion. Calm, neutral expression with a closed mouth, looking straight into the lens. Plain, seamless, light-grey studio background and floor, no horizon line, no scenery. Soft, even, diffuse front lighting with only a faint contact shadow under the feet. Sharp focus on the whole figure. Absolutely no text, letters, numbers, logos, brand names, labels, stickers, price tags, name tags, printed or embroidered patches, flags or insignia anywhere in the image: every garment and every object is plain and unbranded. No furniture of any kind (no tables, counters, desks, chairs, stools, benches, shelves) and no vehicles; the person stands alone and everything that identifies the job is worn or held. No other people. Realistic, clean, ordinary-looking clothes and objects, not a costume, not stylised, not a cartoon, no dramatic pose.

The person: a South Asian man in his late 30s, light-brown skin, long rectangular face with a strong jaw, thick black hair swept back, full dark beard kept short, heavy eyebrows, tall broad-shouldered build.

He is a lumberjack: red-and-black buffalo-check flannel shirt with sleeves rolled to the forearm, dark work trousers with orange chainsaw-protective panels, brown leather lace-up work boots, an orange forestry safety helmet with a mesh visor flipped up and ear defenders resting on the sides. He holds a long-handled wooden felling axe in his right hand, head of the axe resting on the floor beside his right foot, handle upright. Left arm relaxed. No furniture, no logs, no trees.
```

## plongeur

```text
Photorealistic studio photograph, matching the attached reference image exactly in style, framing and lighting. Square 1:1 image. One adult person, full body from the top of the head to the soles of the shoes, centred, standing upright and facing the camera squarely, feet slightly apart, weight on both feet, body taking up about 85% of the image height with a small margin above the head and below the feet. Camera at chest height, straight on, no tilt, no wide-angle distortion. Calm, neutral expression with a closed mouth, looking straight into the lens. Plain, seamless, light-grey studio background and floor, no horizon line, no scenery. Soft, even, diffuse front lighting with only a faint contact shadow under the feet. Sharp focus on the whole figure. Absolutely no text, letters, numbers, logos, brand names, labels, stickers, price tags, name tags, printed or embroidered patches, flags or insignia anywhere in the image: every garment and every object is plain and unbranded. No furniture of any kind (no tables, counters, desks, chairs, stools, benches, shelves) and no vehicles; the person stands alone and everything that identifies the job is worn or held. No other people. Realistic, clean, ordinary-looking clothes and objects, not a costume, not stylised, not a cartoon, no dramatic pose.

The person: a White European man in his mid 20s, fair skin with light freckles across the nose, narrow face with a pointed chin, short wet-looking sandy-blond hair, clean-shaven, light-blue eyes, lean swimmer's build.

He is a scuba diver, recognisable from his gear alone: a full-length black neoprene wetsuit, a black buoyancy vest with a single silver air tank on his back, a regulator hose over his right shoulder, a diving mask pushed up onto his forehead (face fully visible), and black dive boots on his feet (no fins worn, so he can stand normally). Arms relaxed by his sides. No objects in his hands, no water, no furniture.
```

## bijoutier

```text
Photorealistic studio photograph, matching the attached reference image exactly in style, framing and lighting. Square 1:1 image. One adult person, full body from the top of the head to the soles of the shoes, centred, standing upright and facing the camera squarely, feet slightly apart, weight on both feet, body taking up about 85% of the image height with a small margin above the head and below the feet. Camera at chest height, straight on, no tilt, no wide-angle distortion. Calm, neutral expression with a closed mouth, looking straight into the lens. Plain, seamless, light-grey studio background and floor, no horizon line, no scenery. Soft, even, diffuse front lighting with only a faint contact shadow under the feet. Sharp focus on the whole figure. Absolutely no text, letters, numbers, logos, brand names, labels, stickers, price tags, name tags, printed or embroidered patches, flags or insignia anywhere in the image: every garment and every object is plain and unbranded. No furniture of any kind (no tables, counters, desks, chairs, stools, benches, shelves) and no vehicles; the person stands alone and everything that identifies the job is worn or held. No other people. Realistic, clean, ordinary-looking clothes and objects, not a costume, not stylised, not a cartoon, no dramatic pose.

The person: a Black man in his mid 50s, medium-dark brown skin, square face, shaved bald head, clean-shaven, thin wire-rimmed reading glasses, slim build.

He is a jeweller: charcoal-grey waistcoat over a white shirt with sleeves neatly rolled, dark-grey tie, dark trousers, black dress shoes, a jeweller's magnifying loupe on a black headband pushed up onto his forehead. In his right hand, held up at chest height between thumb and finger, a small gold ring with a sparkling diamond. In his left hand, at waist height, an open black velvet jewellery tray holding several gold and silver rings and a fine gold necklace. Nothing else.
```

## chauffeur

```text
Photorealistic studio photograph, matching the attached reference image exactly in style, framing and lighting. Square 1:1 image. One adult person, full body from the top of the head to the soles of the shoes, centred, standing upright and facing the camera squarely, feet slightly apart, weight on both feet, body taking up about 85% of the image height with a small margin above the head and below the feet. Camera at chest height, straight on, no tilt, no wide-angle distortion. Calm, neutral expression with a closed mouth, looking straight into the lens. Plain, seamless, light-grey studio background and floor, no horizon line, no scenery. Soft, even, diffuse front lighting with only a faint contact shadow under the feet. Sharp focus on the whole figure. Absolutely no text, letters, numbers, logos, brand names, labels, stickers, price tags, name tags, printed or embroidered patches, flags or insignia anywhere in the image: every garment and every object is plain and unbranded. No furniture of any kind (no tables, counters, desks, chairs, stools, benches, shelves) and no vehicles; the person stands alone and everything that identifies the job is worn or held. No other people. Realistic, clean, ordinary-looking clothes and objects, not a costume, not stylised, not a cartoon, no dramatic pose.

The person: a White European man in his early 50s, olive-toned Mediterranean skin, long oval face with a prominent nose, short dark-brown hair greying at the temples, neat full grey-and-brown moustache, medium build.

He is a private chauffeur: a black single-breasted suit, white shirt, black tie, black leather driving gloves, polished black shoes, and a black peaked chauffeur's cap with a plain black band (no badge, nothing that looks like a police or pilot cap). In his right gloved hand, raised slightly at chest height, he holds a plain black car key with a remote fob on a short ring. Over his left forearm hangs a folded black umbrella, his left hand loose. No car, nothing else.
```

## menuisier

```text
Photorealistic studio photograph, matching the attached reference image exactly in style, framing and lighting. Square 1:1 image. One adult person, full body from the top of the head to the soles of the shoes, centred, standing upright and facing the camera squarely, feet slightly apart, weight on both feet, body taking up about 85% of the image height with a small margin above the head and below the feet. Camera at chest height, straight on, no tilt, no wide-angle distortion. Calm, neutral expression with a closed mouth, looking straight into the lens. Plain, seamless, light-grey studio background and floor, no horizon line, no scenery. Soft, even, diffuse front lighting with only a faint contact shadow under the feet. Sharp focus on the whole figure. Absolutely no text, letters, numbers, logos, brand names, labels, stickers, price tags, name tags, printed or embroidered patches, flags or insignia anywhere in the image: every garment and every object is plain and unbranded. No furniture of any kind (no tables, counters, desks, chairs, stools, benches, shelves) and no vehicles; the person stands alone and everything that identifies the job is worn or held. No other people. Realistic, clean, ordinary-looking clothes and objects, not a costume, not stylised, not a cartoon, no dramatic pose.

The person: a North African man in his mid 40s, warm light-olive skin, wide face with high cheekbones, short curly dark-brown hair, short dark stubble beard, deep-set brown eyes, stocky muscular build.

He is a carpenter (joiner): a beige canvas work shirt with sleeves rolled up, a heavy brown leather work apron over it, dark work trousers, tan work boots, a flat carpenter's pencil tucked behind his right ear, a folding wooden ruler in the apron pocket. In his right hand he holds a traditional wooden hand plane at waist height, a few curled pale wood shavings still caught in it. With his left hand he holds upright a plank of pale unfinished wood, about as tall as his shoulder, its lower end resting on the floor beside his left foot; the plank does not cover his body.
```

## mécanicien

```text
Photorealistic studio photograph, matching the attached reference image exactly in style, framing and lighting. Square 1:1 image. One adult person, full body from the top of the head to the soles of the shoes, centred, standing upright and facing the camera squarely, feet slightly apart, weight on both feet, body taking up about 85% of the image height with a small margin above the head and below the feet. Camera at chest height, straight on, no tilt, no wide-angle distortion. Calm, neutral expression with a closed mouth, looking straight into the lens. Plain, seamless, light-grey studio background and floor, no horizon line, no scenery. Soft, even, diffuse front lighting with only a faint contact shadow under the feet. Sharp focus on the whole figure. Absolutely no text, letters, numbers, logos, brand names, labels, stickers, price tags, name tags, printed or embroidered patches, flags or insignia anywhere in the image: every garment and every object is plain and unbranded. No furniture of any kind (no tables, counters, desks, chairs, stools, benches, shelves) and no vehicles; the person stands alone and everything that identifies the job is worn or held. No other people. Realistic, clean, ordinary-looking clothes and objects, not a costume, not stylised, not a cartoon, no dramatic pose.

The person: an East Asian man in his mid 30s, light skin, round face with soft features, medium-length straight black hair parted at the side, clean-shaven, black rectangular-framed glasses, average build.

He is a car mechanic: one-piece dark-blue work overalls (coveralls) with long sleeves, a few light grease smudges on the legs and on his forearms, black steel-toe work boots, a red rag hanging from his back pocket. In his right hand, held at waist height, a large chrome adjustable wrench. Left arm relaxed. No car, no furniture.
```

## nonne

```text
Photorealistic studio photograph, matching the attached reference image exactly in style, framing and lighting. Square 1:1 image. One adult person, full body from the top of the head to the soles of the shoes, centred, standing upright and facing the camera squarely, feet slightly apart, weight on both feet, body taking up about 85% of the image height with a small margin above the head and below the feet. Camera at chest height, straight on, no tilt, no wide-angle distortion. Calm, neutral expression with a closed mouth, looking straight into the lens. Plain, seamless, light-grey studio background and floor, no horizon line, no scenery. Soft, even, diffuse front lighting with only a faint contact shadow under the feet. Sharp focus on the whole figure. Absolutely no text, letters, numbers, logos, brand names, labels, stickers, price tags, name tags, printed or embroidered patches, flags or insignia anywhere in the image: every garment and every object is plain and unbranded. No furniture of any kind (no tables, counters, desks, chairs, stools, benches, shelves) and no vehicles; the person stands alone and everything that identifies the job is worn or held. No other people. Realistic, clean, ordinary-looking clothes and objects, not a costume, not stylised, not a cartoon, no dramatic pose.

The person: a White European woman in her mid 40s, fair skin, broad round face with full cheeks, light-brown eyebrows, pale-blue eyes, no make-up, medium build. Her hair is fully hidden by the veil.

She is a Catholic nun, recognisable from her habit alone: a traditional full-length black habit with long sleeves, a white coif framing her face, a black veil falling over her shoulders and back, a simple wooden cross on a cord around her neck, plain black flat shoes. Hands loosely clasped in front of her at waist height. No objects in her hands, no furniture.
```

## bergère

```text
Photorealistic studio photograph, matching the attached reference image exactly in style, framing and lighting. Square 1:1 image. One adult person, full body from the top of the head to the soles of the shoes, centred, standing upright and facing the camera squarely, feet slightly apart, weight on both feet, body taking up about 85% of the image height with a small margin above the head and below the feet. Camera at chest height, straight on, no tilt, no wide-angle distortion. Calm, neutral expression with a closed mouth, looking straight into the lens. Plain, seamless, light-grey studio background and floor, no horizon line, no scenery. Soft, even, diffuse front lighting with only a faint contact shadow under the feet. Sharp focus on the whole figure. Absolutely no text, letters, numbers, logos, brand names, labels, stickers, price tags, name tags, printed or embroidered patches, flags or insignia anywhere in the image: every garment and every object is plain and unbranded. No furniture of any kind (no tables, counters, desks, chairs, stools, benches, shelves) and no vehicles; the person stands alone and everything that identifies the job is worn or held. No other people. Realistic, clean, ordinary-looking clothes and objects, not a costume, not stylised, not a cartoon, no dramatic pose.

The person: a White European woman in her early 50s, fair sun-tanned skin with freckles across the cheeks and fine lines around the eyes, long narrow face with a strong chin, thick wavy chestnut-brown hair streaked with grey in a single low braid over one shoulder, hazel eyes, tall sturdy build.

She is a shepherdess. The single most important element is an unmistakable shepherd's crook, held in her right hand: a long, straight, smooth pale wooden staff, slightly taller than she is, its tip resting on the floor beside her right foot, topped by a large, wide, open, rounded hook (a full half-circle about as wide as her head, like a classic crook or a bishop's crozier), clearly not a walking-cane handle; the hook rises above her head. Over her left forearm hangs a thick, fluffy, freshly shorn white sheep's fleece of raw wool, her left hand under it. She wears a long, heavy, hooded shepherd's cape of undyed grey-brown wool, fastened at the neck and open at the front, reaching her calves; under it a plain cream linen shirt, loose brown canvas trousers and sturdy plain leather farm boots; hood down. On her head, a traditional shepherd's hat: dark-brown felt with a low, round, undented crown and a very broad, flat brim, worn slightly back so her whole face is evenly lit and not shadowed. She must not look like a hiker, traveller or wanderer: no hiking boots, no walking stick, no backpack, no fedora or cowboy hat (no pinched or dented crown, no upturned brim), no coat with toggles. No animals of any kind, no sheep, no dog.
```

## danseuse

```text
Photorealistic studio photograph, matching the attached reference image exactly in style, framing and lighting. Square 1:1 image. One adult person, full body from the top of the head to the soles of the shoes, centred, standing upright and facing the camera squarely, feet slightly apart, weight on both feet, body taking up about 85% of the image height with a small margin above the head and below the feet. Camera at chest height, straight on, no tilt, no wide-angle distortion. Calm, neutral expression with a closed mouth, looking straight into the lens. Plain, seamless, light-grey studio background and floor, no horizon line, no scenery. Soft, even, diffuse front lighting with only a faint contact shadow under the feet. Sharp focus on the whole figure. Absolutely no text, letters, numbers, logos, brand names, labels, stickers, price tags, name tags, printed or embroidered patches, flags or insignia anywhere in the image: every garment and every object is plain and unbranded. No furniture of any kind (no tables, counters, desks, chairs, stools, benches, shelves) and no vehicles; the person stands alone and everything that identifies the job is worn or held. No other people. Realistic, clean, ordinary-looking clothes and objects, not a costume, not stylised, not a cartoon, no dramatic pose.

The person: a Black woman in her mid 20s, deep dark-brown skin, long slender neck, high forehead and defined cheekbones, dark hair pulled into a tight neat ballet bun, small gold stud earrings, tall slender dancer's build.

She is a ballet dancer, recognisable from her outfit alone: a pale-pink sleeveless leotard with an attached stiff classical pale-pink tutu, pink tights, pale-pink satin pointe shoes with ribbons tied around the ankles. She stands flat-footed in a relaxed ballet first position (heels together, toes slightly turned out), arms lowered softly in front of her body in preparatory position. No dance move, no objects, no furniture.
```

## serveuse

```text
Photorealistic studio photograph, matching the attached reference image exactly in style, framing and lighting. Square 1:1 image. One adult person, full body from the top of the head to the soles of the shoes, centred, standing upright and facing the camera squarely, feet slightly apart, weight on both feet, body taking up about 85% of the image height with a small margin above the head and below the feet. Camera at chest height, straight on, no tilt, no wide-angle distortion. Calm, neutral expression with a closed mouth, looking straight into the lens. Plain, seamless, light-grey studio background and floor, no horizon line, no scenery. Soft, even, diffuse front lighting with only a faint contact shadow under the feet. Sharp focus on the whole figure. Absolutely no text, letters, numbers, logos, brand names, labels, stickers, price tags, name tags, printed or embroidered patches, flags or insignia anywhere in the image: every garment and every object is plain and unbranded. No furniture of any kind (no tables, counters, desks, chairs, stools, benches, shelves) and no vehicles; the person stands alone and everything that identifies the job is worn or held. No other people. Realistic, clean, ordinary-looking clothes and objects, not a costume, not stylised, not a cartoon, no dramatic pose.

The person: a South Asian woman in her early 30s, medium-brown skin, heart-shaped face with a small upturned nose, thick dark eyebrows, long straight black hair tied in a high ponytail, dark-brown eyes, slim build.

She is a café waitress: a white long-sleeved shirt, a black waistcoat, black trousers, black flat shoes, and a long black bistro apron tied at the waist reaching below the knee, with a notepad and pen in the apron pocket. With her right hand she holds a round silver serving tray at shoulder height, palm up under it, carrying two white coffee cups on saucers and a glass of water. Left arm relaxed. No furniture.
```

## caissière

```text
Photorealistic studio photograph, matching the attached reference image exactly in style, framing and lighting. Square 1:1 image. One adult person, full body from the top of the head to the soles of the shoes, centred, standing upright and facing the camera squarely, feet slightly apart, weight on both feet, body taking up about 85% of the image height with a small margin above the head and below the feet. Camera at chest height, straight on, no tilt, no wide-angle distortion. Calm, neutral expression with a closed mouth, looking straight into the lens. Plain, seamless, light-grey studio background and floor, no horizon line, no scenery. Soft, even, diffuse front lighting with only a faint contact shadow under the feet. Sharp focus on the whole figure. Absolutely no text, letters, numbers, logos, brand names, labels, stickers, price tags, name tags, printed or embroidered patches, flags or insignia anywhere in the image: every garment and every object is plain and unbranded. No furniture of any kind (no tables, counters, desks, chairs, stools, benches, shelves) and no vehicles; the person stands alone and everything that identifies the job is worn or held. No other people. Realistic, clean, ordinary-looking clothes and objects, not a costume, not stylised, not a cartoon, no dramatic pose.

The person: an East Asian woman in her late 20s, smooth light skin, square face, short chin-length straight black bob, thin gold-rimmed glasses, average build.

She is a supermarket cashier: a dark-green short-sleeved work polo shirt under a dark-green work vest, no name tag, black trousers, black comfortable shoes. In her left hand, held out a little in front of her at waist height and slightly to her left, she holds a clear plastic bag of red apples. On the front of the bag, facing the camera, is one small plain white sticker printed with a black barcode: vertical black bars only, with no digits, letters or logo beneath or around them. This barcode is the only exception to the no-label rule; nothing else in the image carries any marking. In her right hand, at waist height, she holds a black handheld cordless barcode scanner with no markings, its nose pointed down and across at the bag, a thin red laser line falling across the barcode as if she is scanning it. Her eyes still look straight into the lens, and neither the scanner nor the bag hides her face or body. Nothing else.
```

## chanteuse

```text
Photorealistic studio photograph, matching the attached reference image exactly in style, framing and lighting. Square 1:1 image. One adult person, full body from the top of the head to the soles of the shoes, centred, standing upright and facing the camera squarely, feet slightly apart, weight on both feet, body taking up about 85% of the image height with a small margin above the head and below the feet. Camera at chest height, straight on, no tilt, no wide-angle distortion. Calm, neutral expression with a closed mouth, looking straight into the lens. Plain, seamless, light-grey studio background and floor, no horizon line, no scenery. Soft, even, diffuse front lighting with only a faint contact shadow under the feet. Sharp focus on the whole figure. Absolutely no text, letters, numbers, logos, brand names, labels, stickers, price tags, name tags, printed or embroidered patches, flags or insignia anywhere in the image: every garment and every object is plain and unbranded. No furniture of any kind (no tables, counters, desks, chairs, stools, benches, shelves) and no vehicles; the person stands alone and everything that identifies the job is worn or held. No other people. Realistic, clean, ordinary-looking clothes and objects, not a costume, not stylised, not a cartoon, no dramatic pose.

The person: a North African woman in her mid 30s, light-olive skin, long face with a strong straight nose and full eyebrows, very long dark-brown curly hair worn loose past her shoulders, brown eyes, light make-up, medium build.

She is a stage singer: an elegant, modest, ankle-length dark-red evening dress with long sleeves, simple black heels. In her right hand, at chest height (well below her face), she holds a classic silver handheld microphone with a black handle; mouth closed, not singing. Left arm relaxed. No microphone stand, no other objects, no stage lights.
```

## coiffeuse

```text
Photorealistic studio photograph, matching the attached reference image exactly in style, framing and lighting. Square 1:1 image. One adult person, full body from the top of the head to the soles of the shoes, centred, standing upright and facing the camera squarely, feet slightly apart, weight on both feet, body taking up about 85% of the image height with a small margin above the head and below the feet. Camera at chest height, straight on, no tilt, no wide-angle distortion. Calm, neutral expression with a closed mouth, looking straight into the lens. Plain, seamless, light-grey studio background and floor, no horizon line, no scenery. Soft, even, diffuse front lighting with only a faint contact shadow under the feet. Sharp focus on the whole figure. Absolutely no text, letters, numbers, logos, brand names, labels, stickers, price tags, name tags, printed or embroidered patches, flags or insignia anywhere in the image: every garment and every object is plain and unbranded. No furniture of any kind (no tables, counters, desks, chairs, stools, benches, shelves) and no vehicles; the person stands alone and everything that identifies the job is worn or held. No other people. Realistic, clean, ordinary-looking clothes and objects, not a costume, not stylised, not a cartoon, no dramatic pose.

The person: a Latin American woman in her mid 40s, warm tan skin, round face with dimples, short pixie-cut dark-brown hair with subtle caramel highlights, brown eyes, small hoop earrings, medium build.

She is a hairdresser: a black short-sleeved top, black trousers, black flat shoes, and a black hairdresser's waist apron with several combs and a round brush in its pockets. In her right hand, at chest height, she holds open silver hairdressing scissors with a black fine-tooth comb between the same fingers; in her left hand, at waist height, a black professional hairdryer with its cord hanging loose. Nothing else.
```

## couturière

```text
Photorealistic studio photograph, matching the attached reference image exactly in style, framing and lighting. Square 1:1 image. One adult person, full body from the top of the head to the soles of the shoes, centred, standing upright and facing the camera squarely, feet slightly apart, weight on both feet, body taking up about 85% of the image height with a small margin above the head and below the feet. Camera at chest height, straight on, no tilt, no wide-angle distortion. Calm, neutral expression with a closed mouth, looking straight into the lens. Plain, seamless, light-grey studio background and floor, no horizon line, no scenery. Soft, even, diffuse front lighting with only a faint contact shadow under the feet. Sharp focus on the whole figure. Absolutely no text, letters, numbers, logos, brand names, labels, stickers, price tags, name tags, printed or embroidered patches, flags or insignia anywhere in the image: every garment and every object is plain and unbranded. No furniture of any kind (no tables, counters, desks, chairs, stools, benches, shelves) and no vehicles; the person stands alone and everything that identifies the job is worn or held. No other people. Realistic, clean, ordinary-looking clothes and objects, not a costume, not stylised, not a cartoon, no dramatic pose.

The person: a Black woman in her mid 50s, medium-brown skin, wide face with full cheeks, short natural grey-and-black coily hair, small pearl earrings, thin black-framed reading glasses on a chain around her neck, full-figured build.

She is a seamstress (dressmaker): a plain navy-blue knee-length dress with three-quarter sleeves, low black shoes, a yellow cloth tape measure draped around her neck hanging down both sides, a red tomato-shaped pincushion strapped to her left wrist. In her right hand, at waist height, a pair of large black-handled fabric shears. Over her left forearm hangs a length of pale floral fabric, partly cut and held together with visible pins, with a threaded needle stuck in it. Nothing else.
```
