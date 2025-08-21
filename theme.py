"""
theme.py — Thème sombre + image de fond pour l'application
---------------------------------------------------------
- Applique un style sombre cohérent à la plupart des widgets Qt
- Gère un fond d'écran (image) qui se redimensionne proprement
- Fournit des hooks pour repeindre le fond à chaque resize

Astuce :
- Pour "descendre" visuellement le grand titre sur la fenêtre principale
  (QLabel nommé 'titre' dans tes .ui), modifie la propriété CSS `padding-top`
  dans le sélecteur `#titre` ci-dessous.
"""

from PyQt5 import QtGui, QtCore


def _paint_background(widget, pm: QtGui.QPixmap):
    """
    Peint le fond du `widget` :
      - Si `pm` (pixmap) est valide → on l'utilise comme fond (cover)
      - Sinon → on dessine un dégradé sombre de secours

    Notes :
      - KeepAspectRatioByExpanding = type "cover" (remplit toute la zone, quitte à couper)
      - WA_StyledBackground = permet au stylesheet de s'appliquer correctement au fond
    """
    pal = widget.palette()

    if pm and not pm.isNull():
        # Mise à l'échelle "cover" : on remplit toute la surface du widget
        scaled = pm.scaled(
            widget.size(),
            QtCore.Qt.KeepAspectRatioByExpanding,
            QtCore.Qt.SmoothTransformation,
        )
        pal.setBrush(widget.backgroundRole(), QtGui.QBrush(scaled))
    else:
        # Plan B : dégradé vertical sombre si l'image est absente/incorrecte
        grad = QtGui.QLinearGradient(0, 0, 0, widget.height() or 600)
        grad.setColorAt(0.0, QtGui.QColor("#0f1218"))
        grad.setColorAt(1.0, QtGui.QColor("#141a22"))
        pal.setBrush(widget.backgroundRole(), QtGui.QBrush(grad))

    widget.setPalette(pal)
    widget.setAutoFillBackground(True)  # important pour peindre le fond
    widget.setAttribute(QtCore.Qt.WA_StyledBackground, True)  # applique le style au fond


def _update_bg(widget, path):
    """
    Recharge la QPixmap à partir de `path` (si défini) et repeint le fond.
    Appelé initialement puis à chaque redimensionnement du widget.
    """
    pm = QtGui.QPixmap(path) if path else QtGui.QPixmap()
    _paint_background(widget, pm)


def apply_theme(widget, bg_path):
    """
    Applique le thème sombre global + l'image de fond donnée par `bg_path`.

    Conseils :
      - Pour déplacer verticalement le titre (QLabel objectName="titre"),
        ajuste `padding-top` dans le bloc CSS `#titre`.
      - Pour agrandir le titre, décommente / ajoute `font-size` dans `#titre`.
      - Si tu veux un autre "look", tu peux surcharger certains sélecteurs
        dans une feuille de style additionnelle après cet appel.
    """
    widget.setStyleSheet(r'''
        /* Police par défaut pour tout */
        * { font-family: "Segoe UI", "DejaVu Sans", Arial; }

        /* Champs et contrôles usuels */
        QLabel, QLineEdit, QPlainTextEdit, QComboBox, QSpinBox, QPushButton {
            background: rgba(16,17,23,210);
            color: #e6edf3;
            border: 1px solid #2b2f36;
            border-radius: 10px;
        }

        /* --- Titre principal (QLabel dont l'objectName == "titre") --- */
        #titre {
            background: transparent;    /* pas de fond pour laisser voir l'image */
            border: none;
            padding-top: 80px;          /* ↓ Décale le titre vers le bas (augmente si besoin) */
            /* font-size: 22px;         /* ← décommente et ajuste pour agrandir le titre */
            /* font-weight: 600;        /* ← optionnel : renforcer le poids */
            /* letter-spacing: 0.5px;   /* ← optionnel : espacement lettres */
        }

        /* Cases à cocher / radio : texte blanc, fond transparent */
        QCheckBox, QRadioButton {
            color: #e6edf3;
            background: transparent;
        }
        /* Style des carrés ronds de checkbox/radio */
        QCheckBox::indicator, QRadioButton::indicator {
            width: 18px; height: 18px;
            border: 1px solid #2b2f36;
            background: rgba(16,17,23,210);
            margin-right: 6px;
        }
        QCheckBox::indicator:checked, QRadioButton::indicator:checked {
            background: #3a88ff; border-color: #3a88ff;
        }

        /* Tableaux : fond sombre, alternance de lignes, sélection bleutée */
        QTableWidget, QTableView, QAbstractItemView {
            background: rgba(16,17,23,210);
            color: #e6edf3;
            gridline-color: #2b2f36;
            alternate-background-color: rgba(22,24,31,210);
            selection-background-color: #23324a;
            selection-color: #e6edf3;               /* ← texte sélectionné en blanc */
        }
        /* Les items gardent un fond transparent (on voit la ligne alternée) */
        QTableWidget::item, QTableView::item { background-color: transparent; }

        /* >>> IMPORTANT : garder le texte blanc même si l'item est "disabled" <<< */
        QTableWidget::item:disabled,
        QTableView::item:disabled {
            color: #e6edf3;                          /* texte d'items "disabled" en blanc */
        }
        QTableWidget::item:selected:disabled,
        QTableView::item:selected:disabled {
            color: #e6edf3;                          /* texte sélectionné + disabled en blanc */
        }

        /* En-têtes de colonnes/lignes */
        QHeaderView::section {
            background: rgba(16,17,23,230);
            color: #e6edf3;
            border: 1px solid #2b2f36;
            padding: 6px;
        }
        QTableCornerButton::section {
            background: rgba(16,17,23,230);
            border: 1px solid #2b2f36;
        }

        /* Scroll areas / viewport (ex: QPlainTextEdit) */
        QAbstractScrollArea, QAbstractScrollArea::viewport {
            background: rgba(16,17,23,210);
        }

        /* Boutons : padding + survol avec bord bleu */
        QPushButton { padding: 8px 14px; }
        QPushButton:hover { border-color: #3a88ff; }

        /* Menus et barre de menus */
        QMenuBar, QMenu {
            background: rgba(16,17,23,230);
            color: #e6edf3;
        }
        QMenu::item:selected { background: #22395c; }

        /* Barre de statut */
        QStatusBar { background: rgba(16,17,23,230); color: #a7b1c2; }

        /* Boîte de dialogue fichiers (force un fond sombre configurable) */
        QFileDialog QWidget { background: rgba(16,17,23,230); color: #e6edf3; }

        /* Nettoyage visuel des labels internes des QMessageBox pour éviter les halos */
        QMessageBox QLabel#qt_msgbox_label { background: transparent; border: none; }
        QMessageBox QLabel#qt_msgboxex_icon_label,
        QMessageBox QLabel#qt_msgbox_icon_label { background: transparent; border: none; }
    ''')

    # >>> Palette "Disabled" en blanc pour couvrir les cas où Qt utilise la palette désactivée
    pal = widget.palette()
    pal.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Text, QtGui.QColor("#e6edf3"))
    pal.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, QtGui.QColor("#e6edf3"))
    pal.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.HighlightedText, QtGui.QColor("#e6edf3"))
    widget.setPalette(pal)

    # Peindre le fond avec l'image (ou dégradé alternatif)
    _update_bg(widget, bg_path)

    # Hook de redimensionnement : à chaque resize, on recalcule le fond
    orig_resize = getattr(widget, "resizeEvent", None)

    def resizeEvent(ev):
        """
        À chaque redimensionnement du widget :
          - on repasse par _update_bg pour recollider l'image au nouveau viewport
          - on appelle l'ancien resizeEvent si le widget en avait déjà un
        """
        _update_bg(widget, bg_path)
        try:
            if callable(orig_resize):
                orig_resize(ev)
        except Exception:
            # on ignore proprement pour éviter les erreurs si l'ancien handler plante
            pass

    # On remplace le handler de resize par notre wrapper
    widget.resizeEvent = resizeEvent
