# Image prompts for the animal nouns (localizer targets)

One prompt per image, pasted whole into a new ChatGPT chat, so earlier images
don't bleed into the next. No reference image. Square 1:1, like the people and
places; resize to 1254 × 1254 afterwards if needed, and save as
`pictures/<name>.png` with the name below (no accents). Then run
`python3 localizer/make_localizer.py` and `python3 demo/make_demo.py`.

Each animal is shown alone, whole, in its natural habitat, in a calm,
typical pose. Whatever its real size, it fills about the same part of the frame
(about 60% of the width, centred, where the eyes are), so a ladybird is a close-up
and a bull is seen from a few metres. The view shows the features that make the
animal recognisable at a glance, even when the image is shown small; heads face
left where there is a head to turn. The habitat stays behind it, readable but
softer than the animal, so the animal is always the subject. No people, no other
animals, nothing man-made (no fences, buildings, collars, tags or text), and the
same bright, even daylight as the people and places.

| File | Noun | English | Shown as |
|---|---|---|---|
| `canard.png` | canard | duck | mallard duck |
| `lezard.png` | lézard | lizard | common wall lizard |
| `serpent.png` | serpent | snake | grass snake |
| `taureau.png` | taureau | bull | bull |
| `papillon.png` | papillon | butterfly | swallowtail butterfly |
| `sanglier.png` | sanglier | wild boar | wild boar |
| `ecureuil.png` | écureuil | squirrel | red squirrel |
| `perroquet.png` | perroquet | parrot | scarlet macaw |
| `chevre.png` | chèvre | goat | goat |
| `araignee.png` | araignée | spider | garden spider |
| `panthere.png` | panthère | panther | black panther |
| `langouste.png` | langouste | spiny lobster | spiny lobster |
| `grenouille.png` | grenouille | frog | green frog |
| `hirondelle.png` | hirondelle | swallow | barn swallow |
| `coccinelle.png` | coccinelle | ladybird | seven-spot ladybird |
| `sauterelle.png` | sauterelle | grasshopper | green grasshopper |

---

## canard

```text
Photorealistic wildlife photograph of a mallard duck (a drake: glossy green head, white neck ring, yellow bill), in its natural habitat. Square 1:1 image.

Viewpoint: at water level, from the side, the duck seen in full profile facing left. Camera level, no fisheye, no tilt, no dramatic angle. The animal is in sharp focus from end to end; the background is readable but slightly softer.

Composition: the centre of the image must be filled by the animal: the whole duck floating on calm water, its body and head filling the middle of the frame. The animal is whole (nothing cut off by the frame edges), centred, and takes up about 60% of the image width, with a clear margin of habitat all around it. Only one animal.

Habitat, so the scene is readable at a glance even when the image is shown small: a quiet pond with reeds and water lilies along the banks behind it; gentle reflections on the water.

Animal: a healthy, adult, typical example of its kind, in a calm, natural pose, not moving fast, not eating prey, not aggressive, mouth closed.

Lighting: bright, even, natural daylight, like a professional nature photograph. No dramatic shadows, no backlight or silhouette, no sunset or night scene, no lens flare, no coloured filters.

Alone: no people, no body parts, no other animals or insects, and nothing man-made: no fences, buildings, roads, vehicles, boats, collars, tags, rings, feeders or cages.

No text: no readable text, letters, numbers, logos, watermarks, signs or labels anywhere.

Must not be mistaken for a goose or a swan, so keep it small-bodied with the green head and yellow bill.
```

## lézard

```text
Photorealistic wildlife photograph of a common wall lizard (slender, brown-green with a patterned back, long thin tail), in its natural habitat. Square 1:1 image.

Viewpoint: close up at the lizard's level, seen from above at a slight angle, in full profile with the head to the left. Camera level, no fisheye, no tilt, no dramatic angle. The animal is in sharp focus from end to end; the background is readable but slightly softer.

Composition: the centre of the image must be filled by the animal: the whole lizard from snout to tail tip, lying flat on a sun-warmed stone, filling the middle of the frame. The animal is whole (nothing cut off by the frame edges), centred, and takes up about 60% of the image width, with a clear margin of habitat all around it. Only one animal.

Habitat, so the scene is readable at a glance even when the image is shown small: an old dry-stone wall of pale limestone with small tufts of grass and moss in the cracks.

Animal: a healthy, adult, typical example of its kind, in a calm, natural pose, not moving fast, not eating prey, not aggressive, mouth closed.

Lighting: bright, even, natural daylight, like a professional nature photograph. No dramatic shadows, no backlight or silhouette, no sunset or night scene, no lens flare, no coloured filters.

Alone: no people, no body parts, no other animals or insects, and nothing man-made: no fences, buildings, roads, vehicles, boats, collars, tags, rings, feeders or cages.

No text: no readable text, letters, numbers, logos, watermarks, signs or labels anywhere.

Must not be mistaken for a snake, a salamander or a newt, so keep all four legs clearly visible and the skin dry and scaly.
```

## serpent

```text
Photorealistic wildlife photograph of a grass snake (olive-green, with a yellow collar behind the head), in its natural habitat. Square 1:1 image.

Viewpoint: at ground level, slightly from above, the head seen in profile. Camera level, no fisheye, no tilt, no dramatic angle. The animal is in sharp focus from end to end; the background is readable but slightly softer.

Composition: the centre of the image must be filled by the animal: the whole snake loosely coiled, its head raised a little and facing left, the coils filling the middle of the frame. The animal is whole (nothing cut off by the frame edges), centred, and takes up about 60% of the image width, with a clear margin of habitat all around it. Only one animal.

Habitat, so the scene is readable at a glance even when the image is shown small: a forest floor of dry leaves, moss and a fallen branch, with ferns behind.

Animal: a healthy, adult, typical example of its kind, in a calm, natural pose, not moving fast, not eating prey, not aggressive, mouth closed.

Lighting: bright, even, natural daylight, like a professional nature photograph. No dramatic shadows, no backlight or silhouette, no sunset or night scene, no lens flare, no coloured filters.

Alone: no people, no body parts, no other animals or insects, and nothing man-made: no fences, buildings, roads, vehicles, boats, collars, tags, rings, feeders or cages.

No text: no readable text, letters, numbers, logos, watermarks, signs or labels anywhere.

Must not be mistaken for a worm, an eel or a lizard, so show the scaly skin, the forked tongue slightly out, and no legs.
```

## taureau

```text
Photorealistic wildlife photograph of a bull (a large, muscular brown bull with short curved horns), in its natural habitat. Square 1:1 image.

Viewpoint: from the side at shoulder height, the bull in full profile facing left, standing still. Camera level, no fisheye, no tilt, no dramatic angle. The animal is in sharp focus from end to end; the background is readable but slightly softer.

Composition: the centre of the image must be filled by the animal: the whole bull from horns to tail and down to the hooves, filling the middle of the frame. The animal is whole (nothing cut off by the frame edges), centred, and takes up about 60% of the image width, with a clear margin of habitat all around it. Only one animal.

Habitat, so the scene is readable at a glance even when the image is shown small: a green grassy pasture with a few trees and low hills behind.

Animal: a healthy, adult, typical example of its kind, in a calm, natural pose, not moving fast, not eating prey, not aggressive, mouth closed.

Lighting: bright, even, natural daylight, like a professional nature photograph. No dramatic shadows, no backlight or silhouette, no sunset or night scene, no lens flare, no coloured filters.

Alone: no people, no body parts, no other animals or insects, and nothing man-made: no fences, buildings, roads, vehicles, boats, collars, tags, rings, feeders or cages.

No text: no readable text, letters, numbers, logos, watermarks, signs or labels anywhere.

Must not be mistaken for a cow or a calf, so show a massive neck and shoulders and clearly visible horns; no udder, no ear tags, no nose ring, no fence.
```

## papillon

```text
Photorealistic wildlife photograph of a swallowtail butterfly (pale yellow wings with black stripes and small blue and red spots, long tails on the hind wings), in its natural habitat. Square 1:1 image.

Viewpoint: close up, seen from directly above the open wings. Camera level, no fisheye, no tilt, no dramatic angle. The animal is in sharp focus from end to end; the background is readable but slightly softer.

Composition: the centre of the image must be filled by the animal: the whole butterfly with its four wings fully spread flat and symmetrical, resting on a flower, filling the middle of the frame. The animal is whole (nothing cut off by the frame edges), centred, and takes up about 60% of the image width, with a clear margin of habitat all around it. Only one animal.

Habitat, so the scene is readable at a glance even when the image is shown small: a flowering meadow: the purple flower it rests on and a soft green background of grass and other flowers.

Animal: a healthy, adult, typical example of its kind, in a calm, natural pose, not moving fast, not eating prey, not aggressive, mouth closed.

Lighting: bright, even, natural daylight, like a professional nature photograph. No dramatic shadows, no backlight or silhouette, no sunset or night scene, no lens flare, no coloured filters.

Alone: no people, no body parts, no other animals or insects, and nothing man-made: no fences, buildings, roads, vehicles, boats, collars, tags, rings, feeders or cages.

No text: no readable text, letters, numbers, logos, watermarks, signs or labels anywhere.

Must not be mistaken for a moth, so keep the wings open, colourful and patterned, with thin antennae ending in small clubs.
```

## sanglier

```text
Photorealistic wildlife photograph of a wild boar (dark bristly grey-brown coat, long snout, small tusks), in its natural habitat. Square 1:1 image.

Viewpoint: from the side at the boar's head height, in full profile facing left, standing on all four legs. Camera level, no fisheye, no tilt, no dramatic angle. The animal is in sharp focus from end to end; the background is readable but slightly softer.

Composition: the centre of the image must be filled by the animal: the whole boar from snout to tail and down to the hooves, filling the middle of the frame. The animal is whole (nothing cut off by the frame edges), centred, and takes up about 60% of the image width, with a clear margin of habitat all around it. Only one animal.

Habitat, so the scene is readable at a glance even when the image is shown small: an oak forest floor with fallen leaves and acorns, tree trunks behind.

Animal: a healthy, adult, typical example of its kind, in a calm, natural pose, not moving fast, not eating prey, not aggressive, mouth closed.

Lighting: bright, even, natural daylight, like a professional nature photograph. No dramatic shadows, no backlight or silhouette, no sunset or night scene, no lens flare, no coloured filters.

Alone: no people, no body parts, no other animals or insects, and nothing man-made: no fences, buildings, roads, vehicles, boats, collars, tags, rings, feeders or cages.

No text: no readable text, letters, numbers, logos, watermarks, signs or labels anywhere.

Must not be mistaken for a domestic pig, so show the dark bristly coat, the long snout and the small white tusks; no pink skin, no mud pen.
```

## écureuil

```text
Photorealistic wildlife photograph of a red squirrel (russet-red fur, white belly, ear tufts, big bushy tail), in its natural habitat. Square 1:1 image.

Viewpoint: at branch height, the squirrel seen from the side, its head in profile facing left. Camera level, no fisheye, no tilt, no dramatic angle. The animal is in sharp focus from end to end; the background is readable but slightly softer.

Composition: the centre of the image must be filled by the animal: the whole squirrel sitting upright on a thick branch, holding a hazelnut in its front paws, its bushy tail curled up behind its back, filling the middle of the frame. The animal is whole (nothing cut off by the frame edges), centred, and takes up about 60% of the image width, with a clear margin of habitat all around it. Only one animal.

Habitat, so the scene is readable at a glance even when the image is shown small: a pine and oak forest: the branch it sits on and soft green foliage behind.

Animal: a healthy, adult, typical example of its kind, in a calm, natural pose, not moving fast, not eating prey, not aggressive, mouth closed.

Lighting: bright, even, natural daylight, like a professional nature photograph. No dramatic shadows, no backlight or silhouette, no sunset or night scene, no lens flare, no coloured filters.

Alone: no people, no body parts, no other animals or insects, and nothing man-made: no fences, buildings, roads, vehicles, boats, collars, tags, rings, feeders or cages.

No text: no readable text, letters, numbers, logos, watermarks, signs or labels anywhere.

Must not be mistaken for a rat, a chipmunk or a mouse, so show the ear tufts and the big bushy tail clearly.
```

## perroquet

```text
Photorealistic wildlife photograph of a scarlet macaw (bright red body, blue and yellow wings, large curved pale beak), in its natural habitat. Square 1:1 image.

Viewpoint: at branch height, the bird seen from the side at a slight three-quarter angle, its head in profile facing left. Camera level, no fisheye, no tilt, no dramatic angle. The animal is in sharp focus from end to end; the background is readable but slightly softer.

Composition: the centre of the image must be filled by the animal: the whole parrot perched on a branch, from the top of its head to the tip of its long tail, filling the middle of the frame. The animal is whole (nothing cut off by the frame edges), centred, and takes up about 60% of the image width, with a clear margin of habitat all around it. Only one animal.

Habitat, so the scene is readable at a glance even when the image is shown small: a tropical rainforest canopy: green leaves and vines around the branch.

Animal: a healthy, adult, typical example of its kind, in a calm, natural pose, not moving fast, not eating prey, not aggressive, mouth closed.

Lighting: bright, even, natural daylight, like a professional nature photograph. No dramatic shadows, no backlight or silhouette, no sunset or night scene, no lens flare, no coloured filters.

Alone: no people, no body parts, no other animals or insects, and nothing man-made: no fences, buildings, roads, vehicles, boats, collars, tags, rings, feeders or cages.

No text: no readable text, letters, numbers, logos, watermarks, signs or labels anywhere.

Must not be mistaken for any other bird, so show the large hooked beak, the bright red, blue and yellow plumage and the long pointed tail.
```

## chèvre

```text
Photorealistic wildlife photograph of a goat (a white-and-brown domestic goat with curved horns and a small beard), in its natural habitat. Square 1:1 image.

Viewpoint: from the side at the goat's head height, in full profile facing left, standing on all four legs. Camera level, no fisheye, no tilt, no dramatic angle. The animal is in sharp focus from end to end; the background is readable but slightly softer.

Composition: the centre of the image must be filled by the animal: the whole goat from horns to tail and down to the hooves, filling the middle of the frame. The animal is whole (nothing cut off by the frame edges), centred, and takes up about 60% of the image width, with a clear margin of habitat all around it. Only one animal.

Habitat, so the scene is readable at a glance even when the image is shown small: a rocky mountain hillside with short grass and scattered stones, mountains in the distance.

Animal: a healthy, adult, typical example of its kind, in a calm, natural pose, not moving fast, not eating prey, not aggressive, mouth closed.

Lighting: bright, even, natural daylight, like a professional nature photograph. No dramatic shadows, no backlight or silhouette, no sunset or night scene, no lens flare, no coloured filters.

Alone: no people, no body parts, no other animals or insects, and nothing man-made: no fences, buildings, roads, vehicles, boats, collars, tags, rings, feeders or cages.

No text: no readable text, letters, numbers, logos, watermarks, signs or labels anywhere.

Must not be mistaken for a sheep, so show the short smooth coat, the horns and the beard; no wool, no collar, no bell, no fence.
```

## araignée

```text
Photorealistic wildlife photograph of a garden spider (a European cross spider: round brown abdomen with a white cross pattern, eight long banded legs), in its natural habitat. Square 1:1 image.

Viewpoint: close up, facing the web straight on, the spider seen from above its back. Camera level, no fisheye, no tilt, no dramatic angle. The animal is in sharp focus from end to end; the background is readable but slightly softer.

Composition: the centre of the image must be filled by the animal: the whole spider at the centre of its round orb web, its eight legs spread, filling the middle of the frame. The animal is whole (nothing cut off by the frame edges), centred, and takes up about 60% of the image width, with a clear margin of habitat all around it. Only one animal.

Habitat, so the scene is readable at a glance even when the image is shown small: a garden hedge: the web strung between twigs, a soft green background of leaves.

Animal: a healthy, adult, typical example of its kind, in a calm, natural pose, not moving fast, not eating prey, not aggressive, mouth closed.

Lighting: bright, even, natural daylight, like a professional nature photograph. No dramatic shadows, no backlight or silhouette, no sunset or night scene, no lens flare, no coloured filters.

Alone: no people, no body parts, no other animals or insects, and nothing man-made: no fences, buildings, roads, vehicles, boats, collars, tags, rings, feeders or cages.

No text: no readable text, letters, numbers, logos, watermarks, signs or labels anywhere.

Must not be mistaken for an insect or a crab, so show all eight legs clearly and the spiral web around it.
```

## panthère

```text
Photorealistic wildlife photograph of a black panther (a black leopard: sleek all-black coat, faint rosettes, yellow-green eyes), in its natural habitat. Square 1:1 image.

Viewpoint: from the side at the panther's shoulder height, in full profile facing left. Camera level, no fisheye, no tilt, no dramatic angle. The animal is in sharp focus from end to end; the background is readable but slightly softer.

Composition: the centre of the image must be filled by the animal: the whole panther lying along a thick tree branch, head raised, from nose to tail tip, filling the middle of the frame. The animal is whole (nothing cut off by the frame edges), centred, and takes up about 60% of the image width, with a clear margin of habitat all around it. Only one animal.

Habitat, so the scene is readable at a glance even when the image is shown small: a tropical forest: the large tree it rests in and dense green foliage behind.

Animal: a healthy, adult, typical example of its kind, in a calm, natural pose, not moving fast, not eating prey, not aggressive, mouth closed.

Lighting: bright, even, natural daylight, like a professional nature photograph. No dramatic shadows, no backlight or silhouette, no sunset or night scene, no lens flare, no coloured filters.

Alone: no people, no body parts, no other animals or insects, and nothing man-made: no fences, buildings, roads, vehicles, boats, collars, tags, rings, feeders or cages.

No text: no readable text, letters, numbers, logos, watermarks, signs or labels anywhere.

Must not be mistaken for a domestic cat or a puma, so show a large, powerful wild cat with the all-black coat.
```

## langouste

```text
Photorealistic wildlife photograph of a spiny lobster (reddish-brown spiny shell, two very long thick antennae, no large claws), in its natural habitat. Square 1:1 image.

Viewpoint: close up from the side and slightly above, in full profile facing left. Camera level, no fisheye, no tilt, no dramatic angle. The animal is in sharp focus from end to end; the background is readable but slightly softer.

Composition: the centre of the image must be filled by the animal: the whole spiny lobster standing on the rocks, from the tips of its long antennae to its fanned tail, filling the middle of the frame. The animal is whole (nothing cut off by the frame edges), centred, and takes up about 60% of the image width, with a clear margin of habitat all around it. Only one animal.

Habitat, so the scene is readable at a glance even when the image is shown small: a rocky seabed in clear, shallow sea water, with seaweed and a rock crevice behind.

Animal: a healthy, adult, typical example of its kind, in a calm, natural pose, not moving fast, not eating prey, not aggressive, mouth closed.

Lighting: bright, even, natural daylight, like a professional nature photograph. No dramatic shadows, no backlight or silhouette, no sunset or night scene, no lens flare, no coloured filters.

Alone: no people, no body parts, no other animals or insects, and nothing man-made: no fences, buildings, roads, vehicles, boats, collars, tags, rings, feeders or cages.

No text: no readable text, letters, numbers, logos, watermarks, signs or labels anywhere.

Must not be mistaken for a clawed lobster, a crayfish or a shrimp, so show the very long antennae and no big front claws; not cooked, not on a plate.
```

## grenouille

```text
Photorealistic wildlife photograph of a green frog (a bright green European water frog with dark spots and golden eyes), in its natural habitat. Square 1:1 image.

Viewpoint: close up at water level, the frog seen from the side at a slight three-quarter angle, facing left. Camera level, no fisheye, no tilt, no dramatic angle. The animal is in sharp focus from end to end; the background is readable but slightly softer.

Composition: the centre of the image must be filled by the animal: the whole frog sitting on a floating lily pad, filling the middle of the frame. The animal is whole (nothing cut off by the frame edges), centred, and takes up about 60% of the image width, with a clear margin of habitat all around it. Only one animal.

Habitat, so the scene is readable at a glance even when the image is shown small: a pond: other lily pads, calm water and reeds behind.

Animal: a healthy, adult, typical example of its kind, in a calm, natural pose, not moving fast, not eating prey, not aggressive, mouth closed.

Lighting: bright, even, natural daylight, like a professional nature photograph. No dramatic shadows, no backlight or silhouette, no sunset or night scene, no lens flare, no coloured filters.

Alone: no people, no body parts, no other animals or insects, and nothing man-made: no fences, buildings, roads, vehicles, boats, collars, tags, rings, feeders or cages.

No text: no readable text, letters, numbers, logos, watermarks, signs or labels anywhere.

Must not be mistaken for a toad, so keep the skin smooth, shiny and green, with long folded hind legs.
```

## hirondelle

```text
Photorealistic wildlife photograph of a barn swallow (glossy dark-blue back, rusty-red throat, cream belly, long forked tail), in its natural habitat. Square 1:1 image.

Viewpoint: at branch height, the bird seen from the side, its head in profile facing left. Camera level, no fisheye, no tilt, no dramatic angle. The animal is in sharp focus from end to end; the background is readable but slightly softer.

Composition: the centre of the image must be filled by the animal: the whole swallow perched on a thin bare twig, from the top of its head to the tips of its long forked tail, filling the middle of the frame. The animal is whole (nothing cut off by the frame edges), centred, and takes up about 60% of the image width, with a clear margin of habitat all around it. Only one animal.

Habitat, so the scene is readable at a glance even when the image is shown small: a summer countryside: a soft background of green meadow and blue sky.

Animal: a healthy, adult, typical example of its kind, in a calm, natural pose, not moving fast, not eating prey, not aggressive, mouth closed.

Lighting: bright, even, natural daylight, like a professional nature photograph. No dramatic shadows, no backlight or silhouette, no sunset or night scene, no lens flare, no coloured filters.

Alone: no people, no body parts, no other animals or insects, and nothing man-made: no fences, buildings, roads, vehicles, boats, collars, tags, rings, feeders or cages.

No text: no readable text, letters, numbers, logos, watermarks, signs or labels anywhere.

Must not be mistaken for a sparrow or a tit, so show the long forked tail streamers, the pointed wings and the red throat; no wire, no building.
```

## coccinelle

```text
Photorealistic wildlife photograph of a seven-spot ladybird (shiny round red wing cases with seven black spots, black head with two white patches), in its natural habitat. Square 1:1 image.

Viewpoint: close up, seen from above and slightly behind, the ladybird walking towards the left. Camera level, no fisheye, no tilt, no dramatic angle. The animal is in sharp focus from end to end; the background is readable but slightly softer.

Composition: the centre of the image must be filled by the animal: the whole ladybird on a green leaf, filling the middle of the frame. The animal is whole (nothing cut off by the frame edges), centred, and takes up about 60% of the image width, with a clear margin of habitat all around it. Only one animal.

Habitat, so the scene is readable at a glance even when the image is shown small: a garden plant: the leaf it walks on and a soft green background of other leaves.

Animal: a healthy, adult, typical example of its kind, in a calm, natural pose, not moving fast, not eating prey, not aggressive, mouth closed.

Lighting: bright, even, natural daylight, like a professional nature photograph. No dramatic shadows, no backlight or silhouette, no sunset or night scene, no lens flare, no coloured filters.

Alone: no people, no body parts, no other animals or insects, and nothing man-made: no fences, buildings, roads, vehicles, boats, collars, tags, rings, feeders or cages.

No text: no readable text, letters, numbers, logos, watermarks, signs or labels anywhere.

Must not be mistaken for a beetle of another colour or a spider, so keep it bright red, round and shiny with the black spots.
```

## sauterelle

```text
Photorealistic wildlife photograph of a green grasshopper (a great green bush-cricket: bright green body, long antennae, long jumping hind legs), in its natural habitat. Square 1:1 image.

Viewpoint: close up at the insect's level, in full profile facing left. Camera level, no fisheye, no tilt, no dramatic angle. The animal is in sharp focus from end to end; the background is readable but slightly softer.

Composition: the centre of the image must be filled by the animal: the whole grasshopper clinging to a grass stem, from the tips of its antennae to the end of its hind legs, filling the middle of the frame. The animal is whole (nothing cut off by the frame edges), centred, and takes up about 60% of the image width, with a clear margin of habitat all around it. Only one animal.

Habitat, so the scene is readable at a glance even when the image is shown small: a summer meadow: tall grasses and a soft green-and-golden background.

Animal: a healthy, adult, typical example of its kind, in a calm, natural pose, not moving fast, not eating prey, not aggressive, mouth closed.

Lighting: bright, even, natural daylight, like a professional nature photograph. No dramatic shadows, no backlight or silhouette, no sunset or night scene, no lens flare, no coloured filters.

Alone: no people, no body parts, no other animals or insects, and nothing man-made: no fences, buildings, roads, vehicles, boats, collars, tags, rings, feeders or cages.

No text: no readable text, letters, numbers, logos, watermarks, signs or labels anywhere.

Must not be mistaken for a cricket or a praying mantis, so show the long folded jumping hind legs and keep the front legs small.
```
