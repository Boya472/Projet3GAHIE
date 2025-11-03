from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings

def about(request):
    """Affiche la page À propos"""
    return render(request, 'about.html')


def contact(request):
    """Affiche et gère le formulaire de contact avec envoi d'email"""
    if request.method == 'POST':
        nom = request.POST.get('nom')
        email = request.POST.get('email')
        telephone = request.POST.get('telephone')
        sujet = request.POST.get('sujet')
        message_contenu = request.POST.get('message')

        # Message formaté
        message = (
            f"--- Nouveau message de contact ---\n"
            f"Nom : {nom}\n"
            f"Email : {email}\n"
            f"Téléphone : {telephone}\n"
            f"Sujet : {sujet}\n\n"
            f"Message :\n{message_contenu}\n"
        )

        try:
            send_mail(
                sujet,
                message,
                settings.DEFAULT_FROM_EMAIL,  # Expéditeur
                [settings.DEFAULT_FROM_EMAIL],  # Destinataire (toi)
                fail_silently=False,
            )
            messages.success(request, "✅ Votre message a été envoyé avec succès !")
        except Exception as e:
            print(e)
            messages.error(request, "❌ Une erreur est survenue lors de l'envoi du message.")

        return redirect('contact')

    return render(request, 'contact.html')
