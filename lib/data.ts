import type { AppData, Subject } from "./types"

import pai from "@/data/subjects/pai.json"
import pendidikanPancasila from "@/data/subjects/pendidikan-pancasila.json"
import bahasaIndonesia from "@/data/subjects/bahasa-indonesia.json"
import bahasaSunda from "@/data/subjects/bahasa-sunda.json"
import ipa from "@/data/subjects/ipa.json"
import ips from "@/data/subjects/ips.json"
import matematika from "@/data/subjects/matematika.json"
import bahasaArab from "@/data/subjects/bahasa-arab.json"
import bahasaInggris from "@/data/subjects/bahasa-inggris.json"
import prakarya from "@/data/subjects/prakarya.json"
import pjok from "@/data/subjects/pjok.json"

// Each subject lives in its own JSON file under /data/subjects/.
// Add a new subject by dropping a *.json file in that folder, then
// importing it here and pushing it into the array below.
const subjects = [
  pai,
  pendidikanPancasila,
  bahasaIndonesia,
  bahasaSunda,
  ipa,
  ips,
  matematika,
  bahasaArab,
  bahasaInggris,
  prakarya,
  pjok,
] as unknown as Subject[]

export const appData: AppData = {
  app: {
    name: "BravoFormz",
    class: "9B",
    version: "1.0",
  },
  subjects,
}
