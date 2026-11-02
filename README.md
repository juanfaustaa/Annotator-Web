# Chord Annotator

Editor chord lokal ala Chordify untuk mengoreksi hasil prediksi model dan meng-export `.lab`.

## Menjalankan

Butuh Python 3.10+, `ffmpeg`, dan `deno` (dipakai yt-dlp untuk YouTube).

**macOS / Linux**

```bash
brew install python@3.12 ffmpeg deno   # sekali saja (Mac)
./run.sh
```

**Windows** (PowerShell)

```powershell
winget install Python.Python.3.12 Gyan.FFmpeg DenoLand.Deno   # sekali saja
py -3.12 -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\uvicorn server:app --host 127.0.0.1 --port 8765
```

Lalu buka http://127.0.0.1:8765. Run pertama `./run.sh` membuat `.venv` otomatis.
Kalau download YouTube mulai gagal, update yt-dlp: `.venv/bin/pip install -U yt-dlp`.

## Alur

1. Tempel link YouTube → **Muat**. Audio di-download ke `tmp/` (WAV mono), beat dideteksi otomatis.
2. **Import .lab** / **Tempel .lab** hasil prediksi. Tiap kotak beat diberi chord dengan overlap terbesar.
3. Koreksi chord, lalu **Export .lab**. File audio di `tmp/` langsung dihapus setelah export
   (juga saat tab ditutup dan saat server start).

Anotasi tersimpan otomatis di browser per video, jadi kalau tab tertutup, muat link yang sama untuk melanjutkan.

## Edit

- Klik kotak = pilih + lompat ke waktu itu. ⇧-klik/⇧-panah = perluas seleksi. Dobel-klik = pilih satu segmen chord.
- Picker bawah: Root, Jenis (maj, min, 7, maj7, min7, sus2, sus4, dim, aug), Bass (slash chord).
  Chord yang dipilih hanya mengubah kotak terpilih; kotak sesudahnya tetap chord lamanya.
- Keyboard: `Space` play/pause, `Enter` putar dari seleksi, `A–G` root, `#` naik ½, `M` minor/mayor, `7`, `J` maj7,
  `4` sus4, `2` sus2, `N` no-chord, `⌫` gabung ke chord kiri, `L` loop seleksi, `⌘Z` / `⇧⌘Z` undo/redo.
- Grid: tempo ½×/2× kalau deteksi beat salah kecepatan, mode Manual (BPM + beat pertama), resolusi ½ ketuk
  untuk chord yang berganti di tengah ketukan, Geser bar untuk meluruskan ketukan 1.

## Format .lab

`start end label`, 3 desimal, pakai `#` (flat otomatis dikonversi): `A`, `A:min`, `A:maj7`, `A:min7`, `G#7`,
`A:sus4`, `D/F#`, `N`.
