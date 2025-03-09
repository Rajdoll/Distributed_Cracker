Berikut adalah panduan lengkap tentang cara menggunakan Minikube untuk menjalankan klaster Kubernetes lokal, mulai dari instalasi, menjalankan, mengelola aplikasi (berdasarkan kasus Anda dengan cracker-deployment dan worker-deployment), hingga mematikannya ketika selesai digunakan. Saya akan menyesuaikan panduan ini dengan konteks Anda yang menggunakan Windows (dengan WSL2 dan driver Docker).
Langkah-Langkah Penggunaan Minikube
1. Prasyarat
Sebelum mulai, pastikan Anda memiliki alat-alat berikut terinstall di mesin Windows Anda:

    Docker Desktop: Untuk driver Docker (sudah Anda gunakan berdasarkan log sebelumnya).
    Minikube: Alat utama untuk menjalankan klaster lokal.
    kubectl: Alat command-line untuk mengelola Kubernetes.
    WSL2: Backend untuk Docker di Windows (sudah aktif di sistem Anda).

Instalasi (Jika Belum Ada):

    Docker Desktop:
        Unduh dari situs resmi Docker.
        Install dan aktifkan WSL2 sebagai backend (pilih Ubuntu sebagai distro default jika belum ada).
    Minikube:
        Unduh binary Minikube untuk Windows dari GitHub releases.
        Pindahkan minikube.exe ke folder yang ada di PATH (misalnya, C:\Windows\System32), atau jalankan dari direktori tertentu.
        Verifikasi instalasi:

        minikube version

    kubectl:
        Unduh dari situs resmi Kubernetes.
        Pindahkan kubectl.exe ke PATH (misalnya, C:\Windows\System32).
        Verifikasi:

        kubectl version --client

2. Menjalankan Minikube
Setelah semua terinstall, berikut langkah-langkah untuk memulai Minikube:

    Mulai Minikube:
        Buka terminal (PowerShell atau CMD).
        Jalankan perintah untuk memulai klaster dengan driver Docker:

        minikube start --driver=docker --cpus 4 --memory 8192

            --driver=docker: Menggunakan Docker sebagai driver (cocok dengan setup Anda).
            --cpus 4: Alokasi 4 CPU untuk klaster.
            --memory 8192: Alokasi 8GB RAM (sesuaikan dengan kebutuhan aplikasi Anda).
        Output akan menunjukkan proses instalasi klaster, seperti:

        * Starting control plane ...
        * Configuring local host environment ...
        * Done! kubectl is now configured to use "minikube" cluster and "default" namespace by default

    Verifikasi Klaster:
        Cek status Minikube:

        minikube status

            Harusnya:

            host: Running
            kubelet: Running
            apiserver: Running

        Cek node:

        kubectl get nodes

            Output: minikube dengan status Ready.
    Konfigurasi kubectl:
        Minikube otomatis mengatur kubectl untuk menggunakan klaster lokalnya. Verifikasi:

        kubectl cluster-info

            Output akan menunjukkan URL API server Minikube.

3. Menjalankan Aplikasi di Minikube
Sekarang, kita akan menjalankan aplikasi Anda (seperti cracker-deployment dan worker-deployment) menggunakan file konfigurasi yang sudah ada (deployment.yaml dan service.yaml).

    Siapkan File Konfigurasi:
        Pastikan Anda memiliki deployment.yaml dan service.yaml di direktori D:\Project\Distributed_Cracker\kubernetes\ seperti sebelumnya.
    Contoh deployment.yaml (dari Anda):
    ```yaml
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: cracker-deployment
    spec:
      replicas: 1
      selector:
        matchLabels:
          app: cracker
      template:
        metadata:
          labels:
            app: cracker
        spec:
          containers:
            - name: frontend
              image: rajdoll/frontend:latest
              ports:
                - containerPort: 5000
              volumeMounts:
                - name: data-volume
                  mountPath: /data
            - name: backend
              image: rajdoll/backend:latest
              ports:
                - containerPort: 5001
              volumeMounts:
                - name: data-volume
                  mountPath: /data
              env:
                - name: REDIS_HOST
                  value: "cracker-service"
                - name: REDIS_PORT
                  value: "6379"
            - name: redis
              image: redis:alpine
              ports:
                - containerPort: 6379
          volumes:
            - name: data-volume
              persistentVolumeClaim:
                claimName: cracker-data-pvc
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: worker-deployment
    spec:
      replicas: 4
      selector:
        matchLabels:
          app: worker
      template:
        metadata:
          labels:
            app: worker
        spec:
          containers:
            - name: worker
              image: rajdoll/worker:latest
              ports:
                - containerPort: 80
              volumeMounts:
                - name: data-volume
                  mountPath: /data
              env:
                - name: REDIS_HOST
                  value: "cracker-service"
                - name: REDIS_PORT
                  value: "6379"
          volumes:
            - name: data-volume
              persistentVolumeClaim:
                claimName: cracker-data-pvc


    **Contoh `service.yaml`**:
    ```yaml
    apiVersion: v1
    kind: Service
    metadata:
      name: cracker-service
    spec:
      selector:
        app: cracker
      ports:
        - name: frontend
          port: 5000
          targetPort: 5000
          nodePort: 30000
        - name: backend
          port: 5001
          targetPort: 5001
          nodePort: 30001
        - name: redis
          port: 6379
          targetPort: 6379
      type: NodePort

    PVC (jika belum ada):
    yaml

    apiVersion: v1
    kind: PersistentVolumeClaim
    metadata:
      name: cracker-data-pvc
    spec:
      accessModes:
        - ReadWriteMany
      resources:
        requests:
          storage: 1Gi
      storageClassName: standard

    Deploy Aplikasi:
        Pindah ke direktori konfigurasi:

        cd D:\Project\Distributed_Cracker\kubernetes

        Terapkan file konfigurasi:

        kubectl apply -f deployment.yaml
        kubectl apply -f service.yaml
        kubectl apply -f storage.yaml  # Jika ada PVC

    Verifikasi Pod:
        Cek status pod:

        kubectl get pods

            Harusnya menunjukkan cracker-deployment (3/3) dan worker-deployment (1/1 untuk 4 replika).
    Akses Aplikasi:
        Dapatkan URL untuk mengakses aplikasi:

        minikube service cracker-service --url

            Output akan memberikan URL seperti http://127.0.0.1:61370 untuk frontend.
        Buka URL di browser untuk mengakses frontend dan coba unggah file.
    Pantau Log (Opsional):
        Lihat log frontend:

        kubectl logs -f <nama-pod-cracker> -c frontend

        Lihat log backend:

        kubectl logs -f <nama-pod-cracker> -c backend

4. Mengelola Minikube Selama Penggunaan

    Cek Status Klaster:

    minikube status

    Hapus Pod/Deployment (Jika Perlu):

    kubectl delete pod <nama-pod>
    kubectl delete -f deployment.yaml

    Akses Dashboard Kubernetes:

    minikube dashboard

        Ini membuka UI web untuk memantau klaster.

5. Mematikan Minikube
Setelah selesai menggunakan Minikube:

    Hentikan Klaster:
        Matikan klaster tanpa menghapus data:

        minikube stop

            Klaster akan berhenti, tetapi konfigurasi dan pod tetap tersimpan untuk restart berikutnya.
    Hapus Klaster (Opsional):
        Jika Anda ingin menghapus seluruh klaster (termasuk semua pod dan data):

        minikube delete

            Ini akan menghapus klaster sepenuhnya; Anda perlu minikube start lagi untuk membuat klaster baru.
    Verifikasi Penghentian:

    minikube status

        Harusnya menunjukkan Stopped atau Nonexistent jika dihapus.

Catatan Penting

    Sumber Daya: Pastikan Docker Desktop memiliki cukup resource (CPU, RAM) yang dialokasikan di pengaturannya agar Minikube berjalan lancar.
    Driver Docker: Anda menggunakan driver Docker, jadi pastikan Docker Desktop selalu aktif saat Minikube berjalan.
    Port: Jika port seperti 30000 atau 61370 bentrok, Minikube akan memilih port lain atau Anda bisa tentukan manual.

Contoh Flow Lengkap

    Mulai:

    minikube start --driver=docker --cpus 4 --memory 8192

    Deploy:

    cd D:\Project\Distributed_Cracker\kubernetes
    kubectl apply -f deployment.yaml
    kubectl apply -f service.yaml

    Akses:

    minikube service cracker-service --url

        Buka http://127.0.0.1:61370 di browser.
    Hentikan:

    minikube stop

Kesimpulan
Dengan panduan ini, Anda bisa menjalankan Minikube dari awal hingga akhir untuk mengelola aplikasi Anda seperti di Kubernetes produksi, tapi secara lokal. Jika ada langkah yang tidak jelas atau Anda ingin contoh spesifik lainnya, beri tahu saya!