from server import card_manager, print_cards_status
from cursor_signup_service import CursorSignupService
from datetime import datetime
import argparse

def main():
    parser = argparse.ArgumentParser(description='Cursor 卡密管理工具')
    parser.add_argument('--new', action='store_true', help='生成新卡密')
    parser.add_argument('--list', action='store_true', help='列出所有卡密')
    parser.add_argument('--disable', type=str, help='禁用指定卡密')
    parser.add_argument('--enable', type=str, help='启用指定卡密')
    
    args = parser.parse_args()
    
    if args.new:
        card_number = card_manager.generate_card()
        signup_service = CursorSignupService()
        result = signup_service.sign_up_account()
        
        if result['success']:
            # 将账号信息添加到卡密
            account_info = {
                'email': result['email'],
                'password': result['password'],
                'token': result['token'],
                'usage_limit': result['usage_limit'],
                'added_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            card_manager.add_account_to_card(card_number, account_info)
            print(f"已生成新卡密: {card_number}")
        else:
            print(f"生成失败: {result['message']}")
    
    elif args.disable:
        if args.disable in card_manager.cards:
            card_manager.cards[args.disable]['status'] = 'disabled'
            card_manager.save_cards()
            print(f"已禁用卡密: {args.disable}")
        else:
            print(f"卡密不存在: {args.disable}")
    
    elif args.enable:
        if args.enable in card_manager.cards:
            card_manager.cards[args.enable]['status'] = 'active'
            card_manager.save_cards()
            print(f"已启用卡密: {args.enable}")
        else:
            print(f"卡密不存在: {args.enable}")
    
    # 打印当前状态
    print_cards_status()

if __name__ == '__main__':
    main() 