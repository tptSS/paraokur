# ParaOkur proje kuralları
- Statik site: Python (generator/build.py) + Jinja şablonları. Sunucu ekleme.
- Rakamlar yalnızca data/facts.json'dan gelir; hiçbir finansal rakamı uydurma, kaynak ve kontrol tarihi göster. Yatırım tavsiyesi verme.
- Git: main'e ASLA doğrudan push etme. Her iş için yeni branch aç (tasarim/..., icerik/...), commit et, push et ve Pull Request aç.
- data/history.json'a dokunma (bot her saat yazıyor). Branch'i main'den güncel tut.
- Değişiklikten önce python generator/build.py --demo ile test et.
