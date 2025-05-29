;; see also src/tools/editors/emacs.samples for more complete settings

((c-mode . ((c-basic-offset . 4)
            (c-file-style . "bsd")
            (fill-column . 78)
            (indent-tabs-mode . t)
            (tab-width . 4)
            (c-file-offsets (case-label . +) (label . -) (statement-case-open . +))
	    (eval add-hook 'before-save-hook 'delete-trailing-whitespace nil t)))
 (lua-mode . ((indent-tabs-mode . t)
	      (tab-width . 4)
	      (eval add-hook 'before-save-hook 'delete-trailing-whitespace nil t)))
 (sh-mode . ((indent-tabs-mode . t)
	     (tab-width . 4)))
 (css-mode . ((tab-width . 4)
	      (eval add-hook 'before-save-hook 'delete-trailing-whitespace nil t)))
 (dsssl-mode . ((indent-tabs-mode . nil)))
 (nxml-mode . ((indent-tabs-mode . nil)
	       (eval add-hook 'before-save-hook 'delete-trailing-whitespace nil t)))
 (perl-mode . ((perl-indent-level . 4)
               (perl-continued-statement-offset . 4)
               (perl-continued-brace-offset . 4)
               (perl-brace-offset . 0)
               (perl-brace-imaginary-offset . 0)
               (perl-label-offset . -2)
               (indent-tabs-mode . t)
               (tab-width . 4)
	       (eval add-hook 'before-save-hook 'delete-trailing-whitespace nil t)))
 (sgml-mode . ((fill-column . 78)
               (indent-tabs-mode . nil))))

;; c-file-offsets is not marked safe by default, but you can either
;; accept the specific value given as safe always, or do something
;; like this in your .emacs to accept only the simplest offset lists
;; automatically:
;; (defun my-safe-c-file-offsets-p (alist)
;;  (catch 'break
;;    (and (listp alist)
;;         (dolist (elt alist t)
;;           (pcase elt
;;             (`(,(pred symbolp) . ,(or `+ `- `++ `-- `* `/)) t)
;;             (`(,(pred symbolp) . ,(or (pred null) (pred integerp))) t)
;;             (`(,(pred symbolp) . [ ,(pred integerp) ]) t)
;;             (_ (throw 'break nil)))))))
;; (put 'c-file-offsets 'safe-local-variable 'my-safe-c-file-offsets-p)
