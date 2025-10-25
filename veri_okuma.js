// Gerekli modüller
const fs = require('fs');
const csv = require('csv-parser');

// === KULLANICI AYARLARI ===
const dosyaAdi = 'Mehmet_Okuyan.csv'; // Buraya istediğin hocanın dosyasını yazabilirsin (örn: Ahmed_Hulusi.csv)
const tamYol = `C:/Users/abdul/Desktop/1/acikkuran-frontend-main/tum_mealler/Mehmet_Okuyan.csv`;

// === VERİ OKUMA FONKSİYONU ===
function okuMealCSV(dosyaYolu, callback) {
    const results = [];
    fs.createReadStream(dosyaYolu, { encoding: 'utf8' })
        .pipe(csv({ separator: ',' }))
        .on('data', (row) => results.push(row))
        .on('end', () => {
            callback(results);
        });
}

// === KULLANIM ÖRNEKLERİ ===
okuMealCSV(tamYol, (veriler) => {
    console.log('\n=== İlk 5 ayet: ===');
    veriler.slice(0, 5).forEach((ayet) => {
        console.log(
            `Sıra: ${ayet.sıra} | Sure: ${ayet.sure} | Ayet: ${ayet.ayet} | Hoca: ${ayet.hoca}\nMetin: ${ayet.metin}\n`
        );
    });

    // 1. Belirli ayeti getir (örnek: 300. ayet)
    let ayet300 = veriler.find(a => a.sıra == 300);
    if (ayet300) {
        console.log('\n=== 300. AYET ===');
        console.log(`Sıra: ${ayet300.sıra} | Sure: ${ayet300.sure} | Ayet: ${ayet300.ayet}\nMetin: ${ayet300.metin}\n`);
    } else {
        console.log('\n=== 300. AYET BULUNAMADI ===');
    }

    // 2. Anahtar kelimeyle arama (örnek: "rahmet")
    let anahtar = 'rahmet';
    let anahtarAyetler = veriler.filter(a => a.metin && a.metin.includes(anahtar));
    console.log(`\n=== "${anahtar}" Kelimesi Geçen İlk 5 Ayet ===`);
    anahtarAyetler.slice(0, 5).forEach(a =>
        console.log(`${a.sure}:${a.ayet} - ${a.metin}`)
    );

    // 3. İlk 10 ayeti göster
    console.log('\n=== İlk 10 Ayet Kısa Liste ===');
    veriler.slice(0, 10).forEach(a => console.log(`${a.sure}:${a.ayet} - ${a.metin}`));
    
    // 4. Son 10 ayeti göster
    console.log('\n=== Son 10 Ayet Kısa Liste ===');
    veriler.slice(-10).forEach(a => console.log(`${a.sure}:${a.ayet} - ${a.metin}`));
});
