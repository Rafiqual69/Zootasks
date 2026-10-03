            account_entity=self.entity,
            token_hash=_hash_token(token),
            expires_at=timezone.now() + timedelta(minutes=15),
        )
        client = Client(enforce_csrf_checks=True)
        path = reverse("owner_email_verify", kwargs={"token": token})
        response = client.get(path, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Referrer-Policy"], "no-referrer")
        self.assertIn("csrftoken", client.cookies)

        csrf_token = get_token(response.wsgi_request)
        post_response = client.post(
            path,