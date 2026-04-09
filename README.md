# 🌐 Asenkron Subnet Ping & Log API

Bu proje, kullanıcı tarafından girilen bir ağ adresindeki (Subnet) IP'lerin erişilebilirlik durumlarını (Ping) tespit etmek amacıyla geliştirilmiş microservice tabanlı bir REST API uygulamasıdır. 

Yüksek hacimli IP taramalarının sistemi kilitlemesini ve kullanıcıyı bekletmesini önlemek amacıyla **Celery** ile asenkron bir mimari tercih edilmiş; veritabanı yükünü hafifletmek için **Redis Cache** mekanizması entegre edilmiştir.

---

## 🚀 Kullanılan Teknolojiler
* **Backend:** Python 3.11, Django, Django REST Framework (DRF)
* **Asenkron İşleyici:** Celery
* **Mesaj Kuyruğu (Broker):** RabbitMQ
* **Önbellek (Cache):** Redis
* **Veritabanı:** PostgreSQL
* **Konteyner Orkestrasyonu:** Docker & Docker Compose

---

## ⚙️ Kurulum ve Çalıştırma

Proje tamamen Dockerize edilmiştir. Bilgisayarınızda sadece **Docker** ve **Docker Compose** kurulu olması yeterlidir.

1. Proje dizinine gidin.
2. Terminalde aşağıdaki komutu çalıştırın:
   ```bash
   docker-compose up --build
3. Tüm servisler (Web, DB, Redis, RabbitMQ, Celery) ayağa kalktığında API kullanıma hazırdır.
    ```bash
    API Ana Adresi: http://localhost:8000/api/ping-requests/
   
## 📡 API Kullanımı (Endpoints)
1. Yeni Bir Subnet Taraması Başlatmak (POST)

Endpoint: POST /api/ping-requests/

Kullanıcıdan gelen IP/Subnet formatı kontrol edilir. IPv4 için max /24, IPv6 için max /64 maske kısıtlaması vardır.
Geçerli ise işlem Celery kuyruğuna alınır ve anında cevap dönülür.

İstek (Request Body - JSON):
```bash
{
    "subnet": "8.8.8.0/29"
}
```


2. Tarama Sonuçlarını Görüntülemek (GET)
Endpoint: GET /api/ping-requests/<id>/

Celery arka planda işlemleri bitirdiğinde sonuçlar bu adresten çekilir.
Sonuçlar ilk okumadan sonra 5 dakikalığına Redis Cache üzerinde tutularak veritabanı maliyeti sıfıra indirilir.

flowchart TD
    User(Kullanici / Postman) -->|HTTP POST / GET| Web[Django Web Sunucusu]
    Web -->|Kayit ve Okuma| DB[(PostgreSQL)]
    Web -->|Onbellek Okuma / Yazma| Redis[(Redis Cache)]
    Web -->|Gorev Iletimi| MQ[[RabbitMQ]]
    MQ -->|Gorevi Alir| Celery(Celery Worker)
    Celery -->|ICMP Ping| Target((Hedef IPler))
    Celery -->|Toplu Kayit bulk_create| DB

flowchart TD
    Start((Baslangic)) --> Req[Subnet Istegi Gelir]
    Req --> Val{Format Gecerli mi?}
    Val -->|Hayir| Err[HTTP 400 Hata Don] --> Finish((Bitir))
    Val -->|Evet| Save[Veritabanina Kaydet]
    Save --> Queue[Gorevi RabbitMQya Gonder]
    Queue --> Res[Kullaniciya HTTP 201 Don]
    Res --> Worker[Celery Gorevi Alir]
    Worker --> Loop[Subnet Icindeki Her IP Icin]
    Loop --> Ping{IPye Ping At}
    Ping -->|Cevap Var| Act[Aktif Isaretle]
    Ping -->|Cevap Yok| Pas[Pasif Isaretle]
    Act --> Add[Gecici Listeye Ekle]
    Pas --> Add
    Add -->|Dongu Biter| Bulk[DBye Toplu Kaydet]
    Bulk --> Finish
