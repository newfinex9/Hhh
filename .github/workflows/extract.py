import os
import json
import requests

def main():
    # استلام البيانات المرسلة من البوت
    payload_raw = os.environ.get("EVENT_PAYLOAD", "{}")
    payload = json.loads(payload_raw)

    fb_token = payload.get("fb_token")
    page_id = payload.get("page_id")
    source = payload.get("source")
    chat_id = payload.get("chat_id")
    bot_token = payload.get("bot_token")
    count = int(payload.get("count", 1))

    if not all([fb_token, page_id, chat_id, bot_token]):
        print("❌ بيانات ناقصة!")
        return

    keys_result = []

    # استخراج روابط ومفاتيح البث عبر Facebook Graph API
    for i in range(1, count + 1):
        url = f"https://graph.facebook.com/v18.0/{page_id}/live_videos"
        params = {
            "access_token": fb_token,
            "status": "UNPUBLISHED",
            "stream_type": "REGULAR"
        }
        try:
            res = requests.post(url, data=params).json()
            if "id" in res:
                stream_url = res.get("secure_stream_url") or res.get("stream_url")
                keys_result.append(f"🔑 **مفتاح {i}:**\n`{stream_url}`")
            else:
                err_msg = res.get("error", {}).get("message", "فشل الاستخراج")
                keys_result.append(f"❌ **مفتاح {i}:** {err_msg}")
        except Exception as e:
            keys_result.append(f"❌ **مفتاح {i}:** {e}")

    # إرسال المفاتيح المستخرجة إلى التليجرام
    results_text = "\n\n".join(keys_result)
    final_message = f"✅ **تمت معالجة الطلب بنجاح:**\n\n{results_text}\n\n🔗 **المصدر:** `{source}`"
    
    telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    requests.post(telegram_url, json={
        "chat_id": chat_id,
        "text": final_message,
        "parse_mode": "Markdown"
    })

if __name__ == "__main__":
    main()

