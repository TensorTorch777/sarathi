import { AuthForm } from "@/components/auth/AuthForm";
import { GuestOnly } from "@/components/auth/GuestOnly";

export default function LoginPage() {
  return (
    <GuestOnly>
      <AuthForm mode="login" />
    </GuestOnly>
  );
}
