from flask_login import login_required

# ---------- Encuesta ----------
@app.route("/encuesta", methods=["GET", "POST"])
@login_required
def encuesta():
    opciones = ["Python", "JavaScript", "Java", "C#"]
    if request.method == "POST":
        if usuario_ya_voto(int(current_user.id)):
            flash("Ya votaste antes. Gracias.")
            return redirect(url_for("resultados"))
        opcion = request.form.get("opcion")
        if opcion not in opciones:
            flash("Elige una opción válida.")
            return redirect(url_for("encuesta"))
        guardar_voto(int(current_user.id), opcion)
        flash("¡Voto registrado!")
        return redirect(url_for("resultados"))
    ya_voto = usuario_ya_voto(int(current_user.id))
    return render_template("encuesta.html", opciones=opciones, ya_voto=ya_voto)
