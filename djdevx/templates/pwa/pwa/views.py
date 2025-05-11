from django.shortcuts import render


def pwa_manifest(request):
    return render(
        request,
        "manifest.json",
        content_type="application/json",
    )


def pwa_service_worker(request):
    return render(
        request,
        "sw.js",
        content_type="application/javascript",
    )
