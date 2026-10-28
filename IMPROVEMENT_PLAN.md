# AI Tutor (Question Generator) · İyileştirme Planı

Bu dosya, `AI_APP_TUTOR` reposunda çalışacak coding agent için bir brief. Amaç: soru üretme pipeline'ını **prompt'a güvenmek yerine modelin etrafındaki harness'ı güçlendirerek** daha güvenilir, ölçülebilir ve ucuz hale getirmek.

> **Agent'a not:** Aşağıdaki "mevcut durum" bölümü Ali'nin notlarından yazıldı, koddan değil. **Önce kodu oku ve doğrula.** Notla kod çelişirse kod doğrudur. Bir şeyin şeklini (fonksiyon adı, JSON alanı, dosya yolu) tahmin etme, gerçek koda ve gerçek bir çıktıya bak.

---

## 0. Çalışma kuralları

1. **Önce plan, sonra kod.** Her faz için kısa bir plan yaz, onay al, sonra uygula.
2. **Ali'nin kısmı:** topic extraction (regex router, LLM yolu, mapping/alias düzeltme) ve generation → review → revise pipeline'ı. **PDF/OCR ve Docker kısmı ekip arkadaşının (Mehmet).** Ona dokunma, gerekiyorsa sadece arayüzünü kullan ve değişiklik ihtiyacını not et.
3. **Var olan çözümü önce ara.** Groq / model sağlayıcısının structured output, retry, caching desteğini **dokümantasyonundan doğrula**, kendin yazmadan önce. Kütüphane API'sini tahmin etme.
4. **Davranışı bozma.** Her değişiklikten önce ve sonra aynı girdilerle çalıştır, farkı göster.
5. **Gerçek çalıştırmayla doğrula.** "Çalışıyor" demeden önce testleri ve gerçek akışı çalıştır.
6. **Sırları koda gömme.** API key'ler env'den.
7. Kod yorumları ve identifier'lar İngilizce.

---

## 1. Mevcut durum (notlara göre, doğrula)

**Stack:** Python, LLM: GPT-OSS-20B via Groq, Regex.

**Akış (workflow, agent değil: sırayı kod belirliyor):**

1. **Topic extraction / regex router:** Girdi bir konu listesiyse, 979 spesifik konuyu 43 genel alana eşleyen sözlükle **LLM çağırmadan** eşleştiriliyor. Diğer metinler LLM'e gidiyor (temperature 0), çıktısı aynı mapping'le düzeltiliyor.
2. **Generator:** temperature zorluğa göre: easy 0.3, medium 0.5, hard 0.7.
3. **Reviewer:** temperature 0.2, "strict reviewer" rolü, 7 kriter. Status: `accepted` / `revise` / `rejected`. Kural: "prefer revise over rejected".
4. **Reviser:** reviewer feedback'ine göre soruyu yeniden yazıyor.
5. **Döngü:** en fazla 3 round. Ara round'larda `rejected` da reviser'a gidiyor. 3 round sonunda hâlâ `rejected` ise kullanıcıya tekrar denemesi söyleniyor. `revise` ise issues ile onaysız dönüyor.

**JSON işleme (kodda, JSON mode / schema YOK):**

- `clean_llm_json` → ``` işaretlerini temizliyor
- `extract_json_object` → regex `\{.*\}` ile JSON'u çekiyor
- `json.loads` → parse
- Status'un izinli değerlerden biri olup olmadığı kontrol ediliyor
- **Tutarsızlık:** `topic_extractor.py` temizleme yapmadan doğrudan `json.loads` kullanıyor.

**Bilinen sorunlar:**

- Üretilen soruların kalitesi hâlâ tatmin edici değil.
- Reviewer, generator ile aynı model, yani aynı kör noktaları paylaşıyor. (Gerçek bir hatayı yakaladığı oldu: döngü/cycle hatalı bir Kruskal sorusu.)
- Kalite ölçülmüyor. Bir prompt değişikliğinin işleri iyileştirip iyileştirmediği bilinmiyor.
- LLM çağrıları için merkezi bir hata yönetimi (timeout, retry) yok (doğrula).

---

## 2. İlkeler (bütün değişikliklerin arkasındaki fikir)

| İlke | Bu projede anlamı |
|---|---|
| **Prompt yönlendirir, kod garanti eder** | Kritik kurallar (format, izinli değerler, limitler) kodda. Prompt sadece kodun kontrol edemediği şeyler için (rol, ton, örnekler). |
| **Model önerir, kod karar verir** | LLM'in topic çıktısı mapping'de yoksa geçersiz. Genel alanı her zaman mapping belirler. |
| **Schema şekli garanti eder, doğruluğu değil** | Schema'ya ek olarak içerik kodda doğrulanır. |
| **Temperature çeşitliliği belirler, zorluğu değil** | Zorluğu prompt belirler. Yüksek temperature daha çeşitli ama daha hatalı → reviewer bu yüzden var. |
| **Tahmin etme, ölç** | Her adım çıktısını kaydeder (trace). Değişiklikler eval set'le karşılaştırılır. |
| **Her LLM çağrısı tek kapıdan** | Timeout, retry, model seçimi ve maliyet takibi tek modülde. |
| **Kod yapabiliyorsa LLM yapmasın** | Regex router bunun örneği. Aynı fikri yeni yerlerde uygula. |

---

## 3. Fazlar

### Faz 1 (P0) · Tek LLM kapısı + trace

**1.1 `llm_client` modülü (mini gateway).** Bütün LLM çağrıları buradan geçsin.

- Her çağrıya **timeout**.
- **Retry:** 429 ve geçici hatalarda (5xx, timeout) exponential backoff + jitter, sınırlı deneme sayısı. 4xx validation hatalarında retry yok.
- **Adım bazında config:** her adım (`topic_extraction`, `generator`, `reviewer`, `reviser`) kendi model ve temperature'ını config'den alsın, kodda sabit olmasın. Model değiştirmek = config değişikliği.
- Her çağrı için **log:** adım, model, temperature, prompt versiyonu, input/output token, süre, hata.
- Bunu kendin yazmadan önce mevcut bir çözüm (ör. sağlayıcının SDK retry ayarları ya da LiteLLM gibi bir gateway kütüphanesi) işe yarar mı bak. Basit tutmak için kendi küçük wrapper'ın da kabul.

**1.2 Trace (her adım çıktısını kaydeder).** Bir istek için bir `trace_id`. Her adım şunu yazsın:

- girdi (veya hash'i), çıktı, parse sonucu, validation sonucu, round numarası, reviewer status ve issues.
- Amaç: kötü bir soru çıktığında **tahmin etmeden** hangi adımda bozulduğunu görmek:
  1. Topic doğru mu çıkarıldı? (girdi doğru geldi mi)
  2. Generator ne üretti? (doğru okundu/kullanıldı mı)
  3. Reviewer neyi kaçırdı, neyi yakaladı?
- Başlangıç için JSONL dosyası yeterli. Database şart değil.

**1.3 Kodda limitler.** Var olan 3 round limiti kalsın. Ek olarak bir istek başına **toplam LLM çağrı sayısı** ve **toplam süre** limiti. Limite ulaşınca kullanıcıya net bir mesaj.

---

### Faz 2 (P0) · Structured output + içerik validation

**2.1 Schema ile structured output.** Groq'un bu model için structured output / JSON schema desteğini **dokümandan doğrula**.

- Destek varsa generator, reviewer, reviser ve topic extraction çıktıları **schema ile** üretilsin (Pydantic modeli öneririm).
- Destek yoksa: JSON mode + mevcut temizleme fallback olarak kalsın, ama **tek bir ortak parse fonksiyonu** olsun (`topic_extractor.py` tutarsızlığı bu şekilde kapanır).
- Önerilen şekiller (mevcut alanlarla karşılaştır, gerekirse uyarla):

```text
Question:
  question: str            # serbest metin
  options: list[str]       # beklenen şık sayısı kadar
  answer: str              # şıklardan birine karşılık gelen harf/id
  explanation: str         # neden doğru (answer key, bkz. Faz 3)
  difficulty: "easy" | "medium" | "hard"
  topic: str
  general_area: str        # kod mapping'den doldurur, model değil

Review:
  status: "accepted" | "revise" | "rejected"
  issues: list[{criterion: str, problem: str}]
  independent_answer: str | null   # bkz. Faz 3

TopicExtraction:
  topics: list[str]        # boş liste geçerli ("not found")
```

- **Zorunlu alan = uydurma riski.** Model bilmiyorsa uydurmak yerine "yok" diyebilsin: topic extraction'da boş liste geçerli bir cevap olsun ve kullanıcıya "metinde bu listeyle eşleşen konu bulunamadı" denilsin.

**2.2 İçerik validation (kodda, schema'dan sonra).** Şekil doğru olsa bile:

- `answer` gerçekten şıklardan birine karşılık geliyor mu?
- Şıklar birbirinden farklı mı, boş şık var mı?
- `difficulty` istenenle aynı mı?
- `topic` 979'luk listede var mı? `general_area` mapping'den mi geliyor (modelin verdiği değil)?
- Validation başarısızsa: hatayı modele söyleyerek **bir kere** tekrar dene. Yine başarısızsa o soruyu düşür ve trace'e yaz.

---

### Faz 3 (P1) · Reviewer'ı güçlendir

Notlara göre reviewer ile generator aynı model. Kontrol etmek üretmekten kolay, ama aynı kör noktalar paylaşılıyor.

1. **Answer key:** generator her soru için doğru cevabı ve kısa bir çözümü (`explanation`) üretsin.
2. **Bağımsız çözüm:** reviewer önce soruyu **answer key'i görmeden** kendisi çözsün (`independent_answer`), sonra key'le karşılaştırsın. Uyuşmazlık otomatik olarak bir issue olsun. (Kruskal örneğindeki gibi mantık hatalarını yakalamak için.)
3. **Reviewer modeli config'den gelsin:** ileride farklı bir model denemek bir config değişikliği olsun. Varsayılan şimdilik aynı model kalabilir.
4. **Issues yapılandırılmış olsun:** her issue hangi kritere (7 kriterden hangisi) ait, belli olsun. Böylece hangi kriterin en sık başarısız olduğu ölçülebilir.

> CV notu: CV'de "generator → reviewer → reviser loop **with one LLM**" yazıyor. Reviewer'a farklı bir model eklenirse Ali CV'yi güncellemeli. Varsayılanı değiştirmeden önce Ali'ye sor.

---

### Faz 4 (P1) · Eval set

Prompt veya model değişince çıktının **daha iyi mi, yoksa sadece farklı mı** olduğunu ölçmek için.

1. `evals/` klasörü:
   - **Topic extraction vakaları:** girdi metin → beklenen topic(ler). Liste girdileri, serbest metinler ve hiçbir konuyla eşleşmeyen metinler.
   - **Reviewer vakaları:** bilerek **hatalı** sorular (yanlış cevap, iki doğru şık, Kruskal'da cycle gibi mantık hatası, yanlış zorluk) ve doğru sorular. Beklenen status ile birlikte.
   - **Generation vakaları:** topic + zorluk → çıktı otomatik kurallarla ve gerekirse LLM-as-judge ile puanlanır.
2. Küçük başla. Ali'nin manuel testte bulduğu hatalar ilk vakalar olsun.
3. `run_evals.py`: her vakayı birkaç kez çalıştırır (çıktı her seferinde değişebilir), **kategori bazında** puanlar ve bir rapor yazar.
4. Ölçülecekler:
   - Topic extraction doğruluğu
   - **Reviewer'ın bilinen hatalı soruları yakalama oranı** (en önemli metrik)
   - Reviewer'ın doğru soruları gereksiz yere reddetme oranı
   - Ortalama round sayısı, istek başına token ve süre
5. **Karar kuralı:** bir değişiklik, hedeflediği kategori iyileşir ve **hiçbir kategori düşmezse** kabul edilir.

---

### Faz 5 (P2) · Maliyet, hız, güvenlik, feedback

1. **Prompt düzeni (caching için):** sabit kısımlar (rol, kurallar, kriterler, örnekler) prompt'un **başında**, değişen kısımlar (topic, zorluk, kullanıcı metni) **sonunda**. Sağlayıcı prompt caching destekliyorsa ucuzlar, desteklemiyorsa da zararı yok.
2. **Prompt versiyonlama:** prompt'lar koddan ayrı dosyalarda, her birinin bir versiyonu olsun. Versiyon her çıktının trace'ine yazılsın.
3. **Paralellik (gerekirse):** birden fazla soru üretiliyorsa çağrılar async + **aynı anda en fazla N çağrı** (semaphore) ile yapılsın. N config'den gelsin ve provider rate limit'inin altında kalsın. Sınırsız paralellik 429 getirir.
4. **Kullanıcı girdisi = veri, talimat değil:** öğrencinin metni prompt'ta açıkça ayrılmış bir bölümde dursun (delimiter'lar). "Önceki talimatları yok say" gibi içerikler talimat olarak uygulanmasın. Model hiçbir zaman tool ya da sistem ayarı seçmesin.
5. **Feedback döngüsü:** kullanıcı bir soruyu "yanlış / kötü" diye işaretleyebilsin. İşaretlenen sorular trace ile birlikte saklansın ve eval set'e aday olsun.
6. **Temperature yorumu:** koddaki yorumlar ve README "temperature = çeşitlilik, zorluk prompt'tan" diye düzeltilsin. Zor sorular için daha çok çeşitlilik istemek mantıklı, ama zorluğu prompt garanti etmeli.

---

## 4. Bitti tanımı

- [ ] Bütün LLM çağrıları `llm_client` üzerinden, timeout + retry + log ile
- [ ] Her istek için trace dosyası, her adımın çıktısıyla
- [ ] Generator/reviewer/reviser/topic çıktıları schema ile (ya da tek bir ortak parser ile), `topic_extractor.py` tutarsızlığı giderildi
- [ ] İçerik validation kodda, başarısızlıkta bir kere retry
- [ ] Reviewer answer key + bağımsız çözümle çalışıyor
- [ ] `evals/` + `run_evals.py`, kategori bazında rapor, değişiklik öncesi ve sonrası sonuçları kaydedildi
- [ ] Model ve temperature adım bazında config'den
- [ ] README güncel: akış, config, eval nasıl çalıştırılır
- [ ] PDF/OCR ve Docker kısmına dokunulmadı (gerekiyorsa not düşüldü)

---

## 5. Agent'tan istediğim ilk çıktı

Hiç kod değiştirmeden önce:

1. Repo yapısının kısa bir özeti ve yukarıdaki "mevcut durum"un koda göre doğrulanmış hali (farkları listele).
2. Groq'un bu model için structured output, JSON mode ve prompt caching desteği (doküman linkiyle).
3. Faz 1 için uygulama planı: hangi dosyalar değişecek, yeni hangi dosyalar eklenecek.
